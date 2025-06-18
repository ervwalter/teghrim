#!/usr/bin/env python3
"""
Pull entities from Kanka to local filesystem.

This script fetches all entities from Kanka and updates the local entities/ folder,
handling conflicts and deletions carefully. It uses file modification times to detect
local changes and fetches posts together with entities to minimize API calls.
"""

import asyncio
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import yaml
from mcp_kanka import KankaOperations, create_operations


def normalize_filename(name: str) -> str:
    """Normalize a name to a safe filename."""
    safe_name = name.lower()
    # Replace common punctuation and spaces
    safe_name = safe_name.replace("'", "").replace('"', "").replace("'", "").replace("'", "")
    safe_name = safe_name.replace(" - ", "-").replace(" ", "-")
    safe_name = safe_name.replace(".", "").replace(",", "").replace(":", "")
    safe_name = safe_name.replace("(", "").replace(")", "").replace("[", "").replace("]", "")
    # Remove any remaining non-alphanumeric characters except hyphens and underscores
    safe_name = "".join(c for c in safe_name if c.isalnum() or c in "-_")
    # Clean up multiple hyphens
    while "--" in safe_name:
        safe_name = safe_name.replace("--", "-")
    # Remove leading/trailing hyphens
    safe_name = safe_name.strip("-")
    return safe_name


class EntityPuller:
    """Handles pulling entities from Kanka to local filesystem."""
    
    def __init__(self, base_path: Path, preserve_local: bool = False, force_update: bool = False):
        self.base_path = base_path
        self.entities_path = base_path / "entities"
        self.deleted_path = self.entities_path / ".deleted"
        self.operations: Optional[KankaOperations] = None
        self.preserve_local = preserve_local
        self.force_update = force_update
        self.report: Dict[str, List[Dict[str, Any]]] = {
            "new": [],
            "updated": [],
            "conflicts": [],
            "deleted": [],
            "unchanged": [],
            "errors": []
        }
    
    async def initialize(self):
        """Initialize the Kanka operations."""
        self.operations = create_operations()
    
    def _get_entity_path(self, entity_type: str, entity_name: str) -> Path:
        """Get the local path for an entity."""
        safe_name = normalize_filename(entity_name)
        # Handle organization vs organisation folder naming
        folder_name = "organizations" if entity_type == "organization" else f"{entity_type}s"
        return self.entities_path / folder_name / f"{safe_name}.md"
    
    def _parse_local_entity(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse a local entity file and extract frontmatter."""
        try:
            content = file_path.read_text(encoding="utf-8")
            if content.startswith("---\n"):
                parts = content.split("---\n", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1])
                    body = parts[2].strip()
                    return {
                        "frontmatter": frontmatter or {},
                        "content": body,
                        "full_content": content,
                        "mtime": file_path.stat().st_mtime
                    }
            return {
                "frontmatter": {},
                "content": content.strip(),
                "full_content": content,
                "mtime": file_path.stat().st_mtime
            }
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _parse_timestamp(self, timestamp_str: str) -> float:
        """Parse ISO timestamp to float for comparison."""
        # Handle both Z and +00:00 suffixes
        if timestamp_str.endswith("Z"):
            timestamp_str = timestamp_str[:-1] + "+00:00"
        dt = datetime.fromisoformat(timestamp_str)
        return dt.timestamp()
    
    def _format_entity_content(self, entity: Dict[str, Any]) -> str:
        """Format entity data as markdown with frontmatter."""
        # Build frontmatter
        frontmatter = {
            "entity_id": entity.get("entity_id", entity["id"]),
            "name": entity["name"],
            "type": entity.get("type", ""),
            "tags": entity.get("tags", []) if isinstance(entity.get("tags", []), list) else [],
            "is_hidden": entity.get("is_hidden", False)
        }
        
        # Add timestamps
        if entity.get("created_at"):
            frontmatter["created"] = entity["created_at"]
        if entity.get("updated_at"):
            frontmatter["updated"] = entity["updated_at"]
        
        # Add quest-specific fields
        if entity.get("entity_type") == "quest" and "is_completed" in entity:
            frontmatter["is_completed"] = entity.get("is_completed", False)
        
        # Store image_full as image in frontmatter (ignore API's image property)
        if entity.get("image_full"):
            frontmatter["image"] = entity["image_full"]
        
        # Remove empty values
        frontmatter = {k: v for k, v in frontmatter.items() if v or v is False}
        
        # Format content
        content_parts = ["---"]
        content_parts.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip())
        content_parts.append("---")
        content_parts.append("")
        
        # Check if we need to add an H1 header
        entity_type = entity.get("entity_type", "")
        entry_content = entity.get("entry", "").strip()
        
        # Don't touch journals or notes
        if entity_type not in ["journal", "note"] and entry_content:
            # Check if content already starts with an H1
            lines = entry_content.split('\n')
            has_h1 = False
            for line in lines:
                if line.strip():  # First non-empty line
                    if line.strip().startswith('# '):
                        has_h1 = True
                    break
            
            # Only add H1 if there isn't one already
            if not has_h1:
                content_parts.append(f"# {entity['name']}")
                content_parts.append("")
        
        # Add entity content
        if entry_content:
            content_parts.append(entry_content)
        
        return "\n".join(content_parts)
    
    def _format_post_content(self, post: Dict[str, Any], entity_id: int) -> str:
        """Format post data as markdown with frontmatter."""
        frontmatter = {
            "post_id": post["id"],
            "entity_id": entity_id,
            "title": post["name"],
            "is_hidden": post.get("is_hidden", False),
            "created": post.get("created_at"),
        }
        
        # Remove empty values
        frontmatter = {k: v for k, v in frontmatter.items() if v or v is False}
        
        # Format content
        content_parts = ["---"]
        content_parts.append(yaml.dump(frontmatter, default_flow_style=False, sort_keys=False).strip())
        content_parts.append("---")
        content_parts.append("")
        
        # Add post content
        if post.get("entry"):
            content_parts.append(post["entry"].strip())
        
        return "\n".join(content_parts)
    
    async def _fetch_all_entities(self) -> Dict[int, Dict[str, Any]]:
        """Fetch all entities from Kanka."""
        print("Fetching all entities from Kanka...")
        all_entities = {}
        
        # Entity types to fetch
        entity_types = [
            "character", "location", "organization", "race", 
            "creature", "note", "journal", "quest"
        ]
        
        for entity_type in entity_types:
            print(f"  Fetching {entity_type}s with posts...")
            try:
                # Get all entities with full content and posts in one call
                result = await self.operations.find_entities(
                    entity_type=entity_type,
                    include_full=True,  # This now includes posts via related=True
                    limit=0  # Get all
                )
                
                entities = result.get("entities", [])
                for entity in entities:
                    # With include_full=True, posts should be included
                    # Use entity_id field, not id
                    entity_id = entity.get("entity_id", entity.get("id"))
                    all_entities[entity_id] = {
                        **entity,
                        "entity_type": entity_type
                    }
                
                print(f"    Found {len(entities)} {entity_type}s")
                
            except Exception as e:
                print(f"    Error fetching {entity_type}s: {e}")
                self.report["errors"].append({
                    "type": "fetch_error",
                    "entity_type": entity_type,
                    "error": str(e)
                })
        
        print(f"Total entities fetched: {len(all_entities)}")
        return all_entities
    
    def _scan_local_entities(self) -> Tuple[
        Dict[int, Tuple[Path, Dict[str, Any]]], 
        Dict[str, Tuple[Path, Dict[str, Any]]]
    ]:
        """Scan local entities and build maps by entity_id and by name."""
        print("Scanning local entities...")
        entities_by_id = {}
        entities_by_name = {}
        
        for entity_dir in self.entities_path.iterdir():
            if not entity_dir.is_dir() or entity_dir.name.startswith("."):
                continue
            
            # Map folder names to entity types
            entity_type = entity_dir.name.rstrip("s")  # Remove plural
            
            for file_path in entity_dir.glob("*.md"):
                # Skip conflict files
                if file_path.name.endswith((".local.md", ".kanka.md")):
                    continue
                    
                entity_data = self._parse_local_entity(file_path)
                if entity_data:
                    # Add to ID map if it has an entity_id
                    if entity_data["frontmatter"].get("entity_id"):
                        entity_id = entity_data["frontmatter"]["entity_id"]
                        entities_by_id[entity_id] = (file_path, entity_data)
                    
                    # Add to name map using the name from frontmatter
                    name = entity_data["frontmatter"].get("name")
                    if name:
                        # Create a key that includes entity type to avoid name collisions
                        name_key = f"{entity_type}:{name.lower()}"
                        entities_by_name[name_key] = (file_path, entity_data)
        
        print(f"Found {len(entities_by_id)} local entities with entity_ids")
        print(f"Found {len(entities_by_name)} total local entities")
        return entities_by_id, entities_by_name
    
    def _set_file_timestamp(self, file_path: Path, timestamp_str: str):
        """Set file modification time to match Kanka timestamp."""
        timestamp = self._parse_timestamp(timestamp_str)
        os.utime(file_path, (timestamp, timestamp))
    
    async def pull_entities(self):
        """Main pull operation."""
        # Fetch all remote entities
        remote_entities = await self._fetch_all_entities()
        
        # Scan local entities - get both ID and name maps
        local_entities_by_id, local_entities_by_name = self._scan_local_entities()
        
        # Track which local files we've processed
        processed_files = set()
        
        # Process each remote entity
        for entity_id, entity in remote_entities.items():
            # First try to match by entity_id
            if entity_id in local_entities_by_id:
                file_path, local_data = local_entities_by_id[entity_id]
                await self._handle_existing_entity(entity, (file_path, local_data))
                processed_files.add(file_path)
            else:
                # Try to match by name (unpushed entities)
                name_key = f"{entity['entity_type']}:{entity['name'].lower()}"
                if name_key in local_entities_by_name:
                    file_path, local_data = local_entities_by_name[name_key]
                    if file_path not in processed_files:  # Avoid duplicates
                        await self._handle_existing_unpushed_entity(entity, file_path)
                        processed_files.add(file_path)
                else:
                    # This is a new entity from Kanka
                    await self._handle_new_entity(entity)
        
        # Process any local entities that weren't matched (deleted from Kanka)
        if not self.preserve_local:
            for entity_id, (file_path, local_data) in local_entities_by_id.items():
                if file_path not in processed_files:
                    await self._handle_deleted_entity((file_path, local_data))
        else:
            # In preserve mode, just report them as local-only
            for entity_id, (file_path, local_data) in local_entities_by_id.items():
                if file_path not in processed_files:
                    self.report["unchanged"].append({
                        "name": local_data["frontmatter"].get("name", file_path.stem),
                        "type": "preserved-local",
                        "path": str(file_path.relative_to(self.base_path)),
                        "note": "Entity missing from Kanka (preserved due to --preserve-local)"
                    })
        
        # Report on local-only entities (no ID, not matched by name)
        for name_key, (file_path, local_data) in local_entities_by_name.items():
            if file_path not in processed_files and not local_data["frontmatter"].get("entity_id"):
                self.report["unchanged"].append({
                    "name": local_data["frontmatter"].get("name", file_path.stem),
                    "type": "local-only",
                    "path": str(file_path.relative_to(self.base_path))
                })
        
        # Print summary
        self._print_summary()
        
        # Print detailed report
        self._print_report()
    
    async def _handle_existing_unpushed_entity(
        self, 
        remote: Dict[str, Any], 
        file_path: Path
    ):
        """Handle an entity that exists locally but hasn't been pushed to Kanka yet."""
        try:
            # This is a match by name - update the local file with the entity_id
            print(f"Linking unpushed local entity {file_path.name} to Kanka entity ID {remote['entity_id']}")
            
            # Read the current file content
            content = file_path.read_text(encoding="utf-8")
            
            # Update frontmatter with entity_id and timestamps from Kanka
            if content.startswith("---\n"):
                parts = content.split("---\n", 2)
                if len(parts) >= 3:
                    frontmatter = yaml.safe_load(parts[1]) or {}
                    frontmatter["entity_id"] = remote["entity_id"]
                    frontmatter["created"] = remote.get("created_at")
                    frontmatter["updated"] = remote.get("updated_at")
                    
                    # Rebuild the file
                    new_content = "---\n"
                    new_content += yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
                    new_content += "---\n"
                    new_content += parts[2]
                    
                    file_path.write_text(new_content, encoding="utf-8")
                    
                    # Set file timestamp to match Kanka
                    if remote.get("updated_at"):
                        self._set_file_timestamp(file_path, remote["updated_at"])
                    
                    self.report["updated"].append({
                        "name": remote["name"],
                        "type": remote["entity_type"],
                        "path": str(file_path.relative_to(self.base_path)),
                        "action": "linked_to_kanka"
                    })
                    
                    # Also sync posts
                    await self._sync_posts(remote, file_path, conflict=False)
            
        except Exception as e:
            self.report["errors"].append({
                "type": "unpushed_entity_error",
                "entity": remote["name"],
                "error": str(e)
            })
    
    async def _handle_new_entity(self, entity: Dict[str, Any]):
        """Handle a new entity from Kanka."""
        try:
            file_path = self._get_entity_path(entity["entity_type"], entity["name"])
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            content = self._format_entity_content(entity)
            file_path.write_text(content, encoding="utf-8")
            
            # Set file timestamp to match Kanka
            if entity.get("updated_at"):
                self._set_file_timestamp(file_path, entity["updated_at"])
            
            self.report["new"].append({
                "name": entity["name"],
                "type": entity["entity_type"],
                "path": str(file_path.relative_to(self.base_path))
            })
            
            # Also sync posts for new entities
            await self._sync_posts(entity, file_path, conflict=False)
            
        except Exception as e:
            self.report["errors"].append({
                "type": "new_entity_error",
                "entity": entity["name"],
                "error": str(e)
            })
    
    async def _handle_existing_entity(
        self, 
        remote: Dict[str, Any], 
        local_info: Tuple[Path, Dict[str, Any]]
    ):
        """Handle an entity that exists both locally and remotely."""
        file_path, local_data = local_info
        
        try:
            # Get timestamps
            remote_updated = self._parse_timestamp(remote.get("updated_at", ""))
            local_mtime = local_data["mtime"]
            
            # Get the timestamp we set when we last pulled from Kanka
            # This is stored in frontmatter for reference
            local_frontmatter = local_data["frontmatter"]
            last_pull_timestamp = None
            if local_frontmatter.get("updated"):
                try:
                    last_pull_timestamp = self._parse_timestamp(local_frontmatter["updated"])
                except:
                    pass
            
            # Decision logic:
            # 1. If local file hasn't been modified since last pull, safe to update
            # 2. If local file was modified after last pull, check if remote also changed
            
            if last_pull_timestamp is None:
                # No previous pull timestamp, be conservative and create conflict
                if abs(local_mtime - remote_updated) > 60:  # More than 1 minute difference
                    await self._handle_conflict(remote, file_path)
                else:
                    # Timestamps are close, assume it's the same content
                    self.report["unchanged"].append({
                        "name": remote["name"],
                        "type": remote["entity_type"]
                    })
            elif abs(local_mtime - last_pull_timestamp) < 60:  # File not modified locally
                if abs(remote_updated - last_pull_timestamp) < 1 and not self.force_update:  # Remote also unchanged
                    self.report["unchanged"].append({
                        "name": remote["name"],
                        "type": remote["entity_type"]
                    })
                else:
                    # Only remote changed, safe to pull
                    remote_content = self._format_entity_content(remote)
                    file_path.write_text(remote_content, encoding="utf-8")
                    self._set_file_timestamp(file_path, remote["updated_at"])
                    
                    self.report["updated"].append({
                        "name": remote["name"],
                        "type": remote["entity_type"],
                        "path": str(file_path.relative_to(self.base_path))
                    })
                    
                    # Also sync posts
                    await self._sync_posts(remote, file_path, conflict=False)
            else:
                # Local file was modified
                if abs(remote_updated - last_pull_timestamp) < 1:  # Remote unchanged
                    # Only local changed, no action needed
                    self.report["unchanged"].append({
                        "name": remote["name"],
                        "type": remote["entity_type"],
                        "note": "Local changes only"
                    })
                    # Still sync posts in case they changed
                    await self._sync_posts(remote, file_path, conflict=False)
                else:
                    # Both changed - conflict!
                    await self._handle_conflict(remote, file_path)
                
        except Exception as e:
            self.report["errors"].append({
                "type": "update_error",
                "entity": remote["name"],
                "error": str(e)
            })
    
    async def _handle_conflict(self, remote: Dict[str, Any], file_path: Path):
        """Handle a conflict where both local and remote have changed."""
        try:
            # Save both versions
            local_backup = file_path.with_suffix(".local.md")
            kanka_version = file_path.with_suffix(".kanka.md")
            
            # Copy current to .local
            shutil.copy2(file_path, local_backup)
            
            # Write Kanka version to .kanka
            remote_content = self._format_entity_content(remote)
            kanka_version.write_text(remote_content, encoding="utf-8")
            if remote.get("updated_at"):
                self._set_file_timestamp(kanka_version, remote["updated_at"])
            
            self.report["conflicts"].append({
                "name": remote["name"],
                "type": remote["entity_type"],
                "path": str(file_path.relative_to(self.base_path)),
                "local_backup": str(local_backup.relative_to(self.base_path)),
                "kanka_version": str(kanka_version.relative_to(self.base_path))
            })
            
            # Also handle posts with conflicts
            await self._sync_posts(remote, file_path, conflict=True)
            
        except Exception as e:
            self.report["errors"].append({
                "type": "conflict_error",
                "entity": remote["name"],
                "error": str(e)
            })
    
    async def _sync_posts(self, entity: Dict[str, Any], entity_file: Path, conflict: bool = False):
        """Sync posts for an entity."""
        posts = entity.get("posts", [])
        if not posts:
            return
        
        # Create posts directory
        entity_name = entity_file.stem
        posts_dir = entity_file.parent / entity_name
        posts_dir.mkdir(exist_ok=True)
        
        # Track existing post files
        existing_files = set(posts_dir.glob("*.md"))
        seen_files = set()
        
        for post in posts:
            try:
                # Generate filename from post title
                safe_name = normalize_filename(post["name"])
                post_file = posts_dir / f"{safe_name}.md"
                seen_files.add(post_file)
                
                # Format post content
                post_content = self._format_post_content(post, entity["id"])
                
                if conflict and post_file.exists():
                    # Save both versions for conflicts
                    local_backup = post_file.with_suffix(".local.md")
                    kanka_version = post_file.with_suffix(".kanka.md")
                    
                    shutil.copy2(post_file, local_backup)
                    kanka_version.write_text(post_content, encoding="utf-8")
                else:
                    # Write or update post
                    post_file.write_text(post_content, encoding="utf-8")
                    
            except Exception as e:
                print(f"Error syncing post '{post['name']}': {e}")
        
        # Handle posts that were deleted from Kanka
        deleted_posts = existing_files - seen_files
        for post_file in deleted_posts:
            # Skip conflict files
            if post_file.name.endswith((".local.md", ".kanka.md")):
                continue
            # Move to deleted folder
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            deleted_name = f"{timestamp}_{post_file.name}"
            deleted_path = self.deleted_path / "posts" / deleted_name
            deleted_path.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(post_file), str(deleted_path))
    
    async def _handle_deleted_entity(self, local_info: Tuple[Path, Dict[str, Any]]):
        """Handle an entity that was deleted from Kanka."""
        file_path, local_data = local_info
        
        try:
            # Create deleted directory
            self.deleted_path.mkdir(parents=True, exist_ok=True)
            
            # Move file with timestamp
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            deleted_name = f"{timestamp}_{file_path.name}"
            deleted_path = self.deleted_path / deleted_name
            
            shutil.move(str(file_path), str(deleted_path))
            
            # Also move any posts directory
            entity_name = file_path.stem
            posts_dir = file_path.parent / entity_name
            if posts_dir.exists() and posts_dir.is_dir():
                deleted_posts_dir = self.deleted_path / f"{timestamp}_{entity_name}"
                shutil.move(str(posts_dir), str(deleted_posts_dir))
            
            self.report["deleted"].append({
                "name": local_data["frontmatter"].get("name", "Unknown"),
                "original_path": str(file_path.relative_to(self.base_path)),
                "deleted_path": str(deleted_path.relative_to(self.base_path))
            })
            
        except Exception as e:
            self.report["errors"].append({
                "type": "delete_error",
                "path": str(file_path),
                "error": str(e)
            })
    
    def _print_summary(self):
        """Print a summary of the pull operation."""
        print("\nSummary:")
        print(f"  New entities from Kanka: {len(self.report['new'])}")
        print(f"  Updated from Kanka: {len(self.report['updated'])}")
        print(f"  Conflicts: {len(self.report['conflicts'])}")
        print(f"  Deleted from Kanka: {len(self.report['deleted'])}")
        
        # Count different types of unchanged
        local_only = [u for u in self.report['unchanged'] if u.get('type') == 'local-only']
        preserved_local = [u for u in self.report['unchanged'] if u.get('type') == 'preserved-local']
        local_changes = [u for u in self.report['unchanged'] if u.get('note') == 'Local changes only']
        unchanged = len(self.report['unchanged']) - len(local_only) - len(local_changes) - len(preserved_local)
        
        print(f"  Unchanged: {unchanged}")
        if local_changes:
            print(f"  With local changes: {len(local_changes)}")
        if local_only:
            print(f"  Local-only (unpushed): {len(local_only)}")
        if preserved_local:
            print(f"  Preserved local entities: {len(preserved_local)}")
        
        if self.report['errors']:
            print(f"  Errors: {len(self.report['errors'])}")
    
    def _print_report(self):
        """Print a detailed report of operations."""
        print("\n" + "="*60)
        print("DETAILED PULL REPORT")
        print("="*60)
        
        if self.report["new"]:
            print(f"\n✅ NEW ENTITIES ({len(self.report['new'])})")
            for item in self.report["new"]:
                print(f"  - {item['name']} ({item['type']}) -> {item['path']}")
        
        if self.report["updated"]:
            print(f"\n📥 UPDATED FROM KANKA ({len(self.report['updated'])})")
            for item in self.report["updated"]:
                print(f"  - {item['name']} ({item['type']})")
        
        if self.report["conflicts"]:
            print(f"\n⚠️  CONFLICTS ({len(self.report['conflicts'])})")
            for item in self.report["conflicts"]:
                print(f"  - {item['name']} ({item['type']})")
                print(f"    Local: {item['local_backup']}")
                print(f"    Kanka: {item['kanka_version']}")
        
        if self.report["deleted"]:
            print(f"\n🗑️  DELETED FROM KANKA ({len(self.report['deleted'])})")
            for item in self.report["deleted"]:
                print(f"  - {item['name']} -> {item['deleted_path']}")
        
        if self.report["unchanged"]:
            print(f"\n✓ UNCHANGED ({len(self.report['unchanged'])})")
            unchanged_local = [u for u in self.report["unchanged"] if u.get("note") == "Local changes only"]
            if unchanged_local:
                print(f"  Including {len(unchanged_local)} with local changes only")
        
        if self.report["errors"]:
            print(f"\n❌ ERRORS ({len(self.report['errors'])})")
            for item in self.report["errors"]:
                print(f"  - {item['type']}: {item.get('entity', item.get('path', 'Unknown'))}")
                print(f"    {item['error']}")
        
        print("\n" + "="*60)


async def main():
    """Main entry point."""
    import sys
    import base64
    import json
    
    # Check for flags
    preserve_local = "--preserve-local" in sys.argv
    force_update = "--force-update" in sys.argv
    
    # Get the teghrim project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    # Debug: Show user ID from token
    try:
        token = os.getenv("KANKA_TOKEN")
        if token:
            # Decode JWT payload to get user ID
            payload = token.split('.')[1]
            # Add padding if needed for base64 decoding
            payload += '=' * (4 - len(payload) % 4)
            decoded = base64.b64decode(payload)
            user_info = json.loads(decoded)
            user_id = user_info.get("sub", "unknown")
            print(f"🔑 Authenticated as Kanka user ID: {user_id}")
    except Exception as e:
        print(f"⚠️  Could not decode token: {e}")
    
    print(f"Pulling entities from Kanka to {project_root}/entities/")
    if preserve_local:
        print("  ⚠️  Preserve-local mode: Will NOT delete entities missing from Kanka")
        print("     (Use this when Kanka campaign has been reset/cleared)")
    if force_update:
        print("  🔄 Force-update mode: Will update ALL entities with latest structure")
        print("     (Use this to add new fields like is_completed and image properties)")
    
    # Create puller and run
    puller = EntityPuller(project_root, preserve_local=preserve_local, force_update=force_update)
    await puller.initialize()
    await puller.pull_entities()


if __name__ == "__main__":
    asyncio.run(main())