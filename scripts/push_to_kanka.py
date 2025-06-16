#!/usr/bin/env python3
"""
Push local entity changes to Kanka.

This script:
1. Creates new entities in Kanka
2. Updates modified entities
3. Updates local frontmatter with new IDs and timestamps
"""

import asyncio
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

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


class EntityPusher:
    """Handles pushing local entities to Kanka."""
    
    def __init__(self, base_path: Path, force_repush: bool = False):
        self.base_path = base_path
        self.entities_path = base_path / "entities"
        self.operations: Optional[KankaOperations] = None
        self.force_repush = force_repush
        self.report: Dict[str, List[Dict[str, Any]]] = {
            "created": [],
            "updated": [],
            "posts_created": [],
            "posts_updated": [],
            "errors": []
        }
    
    async def initialize(self):
        """Initialize the Kanka operations."""
        self.operations = create_operations()
    
    def _parse_entity_file(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Parse an entity file and extract data."""
        try:
            content = file_path.read_text(encoding="utf-8")
            
            if not content.startswith("---\n"):
                return None
            
            parts = content.split("---\n", 2)
            if len(parts) < 3:
                return None
            
            frontmatter = yaml.safe_load(parts[1]) or {}
            body = parts[2].strip()
            
            # Determine entity type from path
            entity_type = file_path.parent.name.rstrip("s")  # Remove plural
            
            return {
                "frontmatter": frontmatter,
                "content": body,
                "entity_type": entity_type,
                "file_path": file_path
            }
            
        except Exception as e:
            print(f"Error parsing {file_path}: {e}")
            return None
    
    def _update_frontmatter(self, file_path: Path, updates: Dict[str, Any]):
        """Update the frontmatter of a file."""
        content = file_path.read_text(encoding="utf-8")
        parts = content.split("---\n", 2)
        
        if len(parts) >= 3:
            frontmatter = yaml.safe_load(parts[1]) or {}
            frontmatter.update(updates)
            
            # Rebuild the file
            new_content = "---\n"
            new_content += yaml.dump(frontmatter, default_flow_style=False, sort_keys=False)
            new_content += "---\n"
            new_content += parts[2]
            
            file_path.write_text(new_content, encoding="utf-8")
            
            # Set file timestamp to match updated timestamp
            if "updated" in updates:
                timestamp = datetime.fromisoformat(
                    updates["updated"].replace("Z", "+00:00")
                ).timestamp()
                os.utime(file_path, (timestamp, timestamp))
    
    async def push_new_entity(self, file_path: Path):
        """Push a new entity to Kanka."""
        entity_data = self._parse_entity_file(file_path)
        if not entity_data:
            self.report["errors"].append({
                "path": str(file_path.relative_to(self.base_path)),
                "error": "Failed to parse file"
            })
            return
        
        frontmatter = entity_data["frontmatter"]
        
        try:
            # Prepare entity data
            # Use name from frontmatter, fallback to stem
            name = frontmatter.get("name", file_path.stem)
            
            create_data = {
                "entity_type": entity_data["entity_type"],
                "name": name,
                "entry": entity_data["content"],
                "type": frontmatter.get("type"),
                "tags": frontmatter.get("tags", []),
                "is_hidden": frontmatter.get("is_hidden", False)
            }
            
            # Add quest-specific fields
            if entity_data["entity_type"] == "quest" and "is_completed" in frontmatter:
                create_data["is_completed"] = frontmatter.get("is_completed", False)
            
            # Create entity
            result = await self.operations.create_entities([create_data])
            
            if result and result[0]["success"]:
                created = result[0]
                
                # Update frontmatter with new ID and timestamps
                updates = {
                    "entity_id": created["entity_id"],
                    "created": datetime.now(timezone.utc).isoformat(),
                    "updated": datetime.now(timezone.utc).isoformat()
                }
                
                self._update_frontmatter(file_path, updates)
                
                self.report["created"].append({
                    "name": created["name"],
                    "entity_id": created["entity_id"],
                    "path": str(file_path.relative_to(self.base_path))
                })
                
                # Push posts for the newly created entity
                await self.push_posts(file_path, created["entity_id"])
            else:
                error = result[0].get("error", "Unknown error") if result else "No result"
                self.report["errors"].append({
                    "path": str(file_path.relative_to(self.base_path)),
                    "error": f"Failed to create: {error}"
                })
                
        except Exception as e:
            self.report["errors"].append({
                "path": str(file_path.relative_to(self.base_path)),
                "error": str(e)
            })
    
    async def push_modified_entity(self, file_path: Path):
        """Push modifications to an existing entity."""
        entity_data = self._parse_entity_file(file_path)
        if not entity_data:
            self.report["errors"].append({
                "path": str(file_path.relative_to(self.base_path)),
                "error": "Failed to parse file"
            })
            return
        
        frontmatter = entity_data["frontmatter"]
        entity_id = frontmatter.get("entity_id")
        
        if not entity_id:
            # No entity_id, treat as new
            await self.push_new_entity(file_path)
            return
        
        try:
            # Prepare update data
            # Use name from frontmatter, fallback to stem
            name = frontmatter.get("name", file_path.stem)
            
            update_data = {
                "entity_id": entity_id,
                "name": name,
                "entry": entity_data["content"],
                "type": frontmatter.get("type"),
                "tags": frontmatter.get("tags", []),
                "is_hidden": frontmatter.get("is_hidden", False)
            }
            
            # Add quest-specific fields
            if entity_data["entity_type"] == "quest" and "is_completed" in frontmatter:
                update_data["is_completed"] = frontmatter.get("is_completed", False)
            
            # Update entity
            result = await self.operations.update_entities([update_data])
            
            if result and result[0]["success"]:
                # Update frontmatter timestamp
                updates = {
                    "updated": datetime.now(timezone.utc).isoformat()
                }
                
                self._update_frontmatter(file_path, updates)
                
                self.report["updated"].append({
                    "name": frontmatter.get("name", file_path.stem),
                    "entity_id": entity_id,
                    "path": str(file_path.relative_to(self.base_path))
                })
                
                # Push posts for the updated entity
                await self.push_posts(file_path, entity_id)
            else:
                error = result[0].get("error", "Unknown error") if result else "No result"
                self.report["errors"].append({
                    "path": str(file_path.relative_to(self.base_path)),
                    "error": f"Failed to update: {error}"
                })
                
        except Exception as e:
            self.report["errors"].append({
                "path": str(file_path.relative_to(self.base_path)),
                "error": str(e)
            })
    
    async def push_posts(self, entity_path: Path, entity_id: int):
        """Push posts for an entity."""
        # Check if entity has a posts directory
        posts_dir = entity_path.parent / entity_path.stem
        if not posts_dir.exists() or not posts_dir.is_dir():
            return
        
        # Process each post file
        for post_file in posts_dir.glob("*.md"):
            await self.push_single_post(post_file, entity_id)
    
    async def push_single_post(self, post_file: Path, entity_id: int):
        """Push a single post file."""
        try:
            content = post_file.read_text(encoding="utf-8")
            
            if not content.startswith("---\n"):
                # No frontmatter, treat as new post
                await self.push_new_post(post_file, entity_id)
                return
            
            parts = content.split("---\n", 2)
            if len(parts) < 3:
                return
            
            frontmatter = yaml.safe_load(parts[1]) or {}
            post_content = parts[2].strip()
            
            if self.force_repush or not frontmatter.get("post_id"):
                # Force repush or no post_id - treat as new
                await self.push_new_post(post_file, entity_id, frontmatter, post_content)
            else:
                # Update existing post
                await self.push_modified_post(post_file, entity_id, frontmatter, post_content)
                
        except Exception as e:
            self.report["errors"].append({
                "path": str(post_file.relative_to(self.base_path)),
                "error": f"Post error: {str(e)}"
            })
    
    async def push_new_post(self, post_file: Path, entity_id: int, frontmatter: Optional[Dict] = None, content: Optional[str] = None):
        """Create a new post in Kanka."""
        try:
            if frontmatter is None or content is None:
                # Parse the file
                file_content = post_file.read_text(encoding="utf-8")
                if file_content.startswith("---\n"):
                    parts = file_content.split("---\n", 2)
                    frontmatter = yaml.safe_load(parts[1]) if len(parts) > 1 else {}
                    content = parts[2].strip() if len(parts) > 2 else ""
                else:
                    frontmatter = {}
                    content = file_content.strip()
            
            # Get post title from frontmatter or filename
            title = frontmatter.get("title", post_file.stem.replace("-", " ").title())
            
            post_data = {
                "entity_id": entity_id,
                "name": title,
                "entry": content,
                "is_hidden": frontmatter.get("is_hidden", False)
            }
            
            result = await self.operations.create_posts([post_data])
            
            if result and result[0]["success"]:
                created = result[0]
                
                # Update frontmatter with post_id
                updates = {
                    "post_id": created["post_id"],
                    "entity_id": entity_id,
                    "title": title
                }
                
                self._update_frontmatter(post_file, updates)
                
                self.report["posts_created"].append({
                    "title": title,
                    "post_id": created["post_id"],
                    "entity_id": entity_id,
                    "path": str(post_file.relative_to(self.base_path))
                })
            else:
                error = result[0].get("error", "Unknown error") if result else "No result"
                self.report["errors"].append({
                    "path": str(post_file.relative_to(self.base_path)),
                    "error": f"Failed to create post: {error}"
                })
                
        except Exception as e:
            self.report["errors"].append({
                "path": str(post_file.relative_to(self.base_path)),
                "error": f"Post creation error: {str(e)}"
            })
    
    async def push_modified_post(self, post_file: Path, entity_id: int, frontmatter: Dict, content: str):
        """Update an existing post in Kanka."""
        try:
            post_id = frontmatter["post_id"]
            title = frontmatter.get("title", post_file.stem.replace("-", " ").title())
            
            update_data = {
                "entity_id": entity_id,
                "post_id": post_id,
                "name": title,
                "entry": content,
                "is_hidden": frontmatter.get("is_hidden", False)
            }
            
            result = await self.operations.update_posts([update_data])
            
            if result and result[0]["success"]:
                self.report["posts_updated"].append({
                    "title": title,
                    "post_id": post_id,
                    "entity_id": entity_id,
                    "path": str(post_file.relative_to(self.base_path))
                })
            else:
                error = result[0].get("error", "Unknown error") if result else "No result"
                self.report["errors"].append({
                    "path": str(post_file.relative_to(self.base_path)),
                    "error": f"Failed to update post: {error}"
                })
                
        except Exception as e:
            self.report["errors"].append({
                "path": str(post_file.relative_to(self.base_path)),
                "error": f"Post update error: {str(e)}"
            })
    
    async def push_changes(self, paths: List[Path]):
        """Push a list of entity and post files to Kanka."""
        # Separate entity files and post files
        entity_files = []
        post_files = []
        
        for path in paths:
            # Check if this is a post file (inside an entity directory)
            if path.parent.parent.name in ["characters", "locations", "organizations", "races", "creatures", "notes", "journals", "quests"]:
                # This is a post file
                post_files.append(path)
            else:
                # This is an entity file
                entity_files.append(path)
        
        # Push entities first
        if entity_files:
            print(f"Pushing {len(entity_files)} entities to Kanka...")
            for i, path in enumerate(entity_files, 1):
                print(f"  [{i}/{len(entity_files)}] {path.name}...")
                
                # Check if it's a new or modified entity
                entity_data = self._parse_entity_file(path)
                if self.force_repush or not (entity_data and entity_data["frontmatter"].get("entity_id")):
                    # Force repush or no entity_id - treat as new
                    await self.push_new_entity(path)
                else:
                    await self.push_modified_entity(path)
        
        # Push individual post files
        if post_files:
            print(f"\nPushing {len(post_files)} posts to Kanka...")
            for i, path in enumerate(post_files, 1):
                print(f"  [{i}/{len(post_files)}] {path.name}...")
                
                # Find the parent entity
                entity_dir = path.parent
                entity_name = entity_dir.name
                entity_type = entity_dir.parent.name
                
                # Look for the entity file
                entity_file = entity_dir.parent / f"{entity_name}.md"
                if entity_file.exists():
                    entity_data = self._parse_entity_file(entity_file)
                    if entity_data and entity_data["frontmatter"].get("entity_id"):
                        await self.push_single_post(path, entity_data["frontmatter"]["entity_id"])
                    else:
                        self.report["errors"].append({
                            "path": str(path.relative_to(self.base_path)),
                            "error": "Parent entity has no entity_id"
                        })
                else:
                    self.report["errors"].append({
                        "path": str(path.relative_to(self.base_path)),
                        "error": "Parent entity file not found"
                    })
        
        self._print_report()
    
    def _print_report(self):
        """Print a summary report."""
        print("\n" + "="*60)
        print("PUSH REPORT")
        print("="*60)
        
        if self.report["created"]:
            print(f"\n✅ CREATED ({len(self.report['created'])})")
            for item in self.report["created"]:
                print(f"  - {item['name']} (ID: {item['entity_id']})")
                print(f"    {item['path']}")
        
        if self.report["updated"]:
            print(f"\n📤 UPDATED ({len(self.report['updated'])})")
            for item in self.report["updated"]:
                print(f"  - {item['name']} (ID: {item['entity_id']})")
        
        if self.report["posts_created"]:
            print(f"\n📝 POSTS CREATED ({len(self.report['posts_created'])})")
            for item in self.report["posts_created"]:
                print(f"  - {item['title']} (Post ID: {item['post_id']})")
                print(f"    Entity ID: {item['entity_id']}")
                print(f"    {item['path']}")
        
        if self.report["posts_updated"]:
            print(f"\n✏️  POSTS UPDATED ({len(self.report['posts_updated'])})")
            for item in self.report["posts_updated"]:
                print(f"  - {item['title']} (Post ID: {item['post_id']})")
        
        if self.report["errors"]:
            print(f"\n❌ ERRORS ({len(self.report['errors'])})")
            for item in self.report["errors"]:
                print(f"  - {item['path']}")
                print(f"    {item['error']}")
        
        print("\n" + "="*60)
        
        # Summary
        total_entities = len(self.report["created"]) + len(self.report["updated"])
        total_posts = len(self.report["posts_created"]) + len(self.report["posts_updated"])
        
        if total_entities > 0 or total_posts > 0:
            summary = []
            if total_entities > 0:
                summary.append(f"{total_entities} entities")
            if total_posts > 0:
                summary.append(f"{total_posts} posts")
            print(f"\nSuccessfully pushed {' and '.join(summary)}")


async def main():
    """Main entry point."""
    import sys
    
    # Check for file arguments
    if len(sys.argv) < 2:
        print("Usage: python push_to_kanka.py <file1.md> [file2.md] ...")
        print("       python push_to_kanka.py --all  # Push all local changes")
        print("       python push_to_kanka.py --force-repush <file1.md> ...  # Force recreate entities")
        print("       python push_to_kanka.py --all --force-repush  # Force recreate ALL entities")
        print("\nOr use with find_local_changes.py:")
        print("  python find_local_changes.py  # Find what needs pushing")
        print("  python push_to_kanka.py entities/characters/gandalf.md")
        return
    
    # Check for --force-repush flag
    force_repush = "--force-repush" in sys.argv
    if force_repush:
        sys.argv.remove("--force-repush")
    
    # Get the project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    paths = []
    
    # Check for --all flag
    if "--all" in sys.argv:
        if force_repush:
            # Force repush ALL entities
            print("  ⚠️  Force-repush mode: Will recreate ALL entities in Kanka")
            print("     (Use this when Kanka campaign has been reset/cleared)")
            
            # Find ALL entities, not just changed ones
            for entity_dir in (project_root / "entities").iterdir():
                if entity_dir.is_dir() and not entity_dir.name.startswith("."):
                    for file_path in entity_dir.glob("*.md"):
                        if not file_path.name.endswith((".local.md", ".kanka.md")):
                            paths.append(file_path)
            
            print(f"\nFound {len(paths)} total entities to force repush")
        else:
            # Find all entities with local changes
            from find_local_changes import LocalChangeFinder
            
            finder = LocalChangeFinder(project_root)
            finder.find_changes()
            
            # Collect all paths that need pushing
            for entity in finder.new_entities:
                path = project_root / entity["path"]
                if path.exists():
                    paths.append(path)
            
            for entity in finder.modified_entities:
                path = project_root / entity["path"]
                if path.exists():
                    paths.append(path)
            
            if not paths:
                print("\nNo local changes to push!")
                return
                
            print(f"\nFound {len(paths)} entities to push")
    else:
        # Convert arguments to paths
        for arg in sys.argv[1:]:
            path = Path(arg)
            if not path.is_absolute():
                path = project_root / path
            
            if path.exists() and path.suffix == ".md":
                paths.append(path)
            else:
                print(f"Warning: Skipping {arg} (not found or not .md)")
        
        if not paths:
            print("No valid files to push")
            return
    
    if force_repush:
        print("\n⚠️  FORCE REPUSH MODE ACTIVE ⚠️")
        print("This will recreate all entities with new IDs!")
        response = input("Continue? (yes/no): ")
        if response.lower() != "yes":
            print("Aborted.")
            return
    
    # Create pusher and run
    pusher = EntityPusher(project_root, force_repush=force_repush)
    await pusher.initialize()
    await pusher.push_changes(paths)


if __name__ == "__main__":
    asyncio.run(main())