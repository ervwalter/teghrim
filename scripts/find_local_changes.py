#!/usr/bin/env python3
"""
Find local entity changes that need to be pushed to Kanka.

This script identifies:
- New entities (no entity_id in frontmatter)
- Modified entities (file mtime > frontmatter updated timestamp)
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple

import yaml


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


class LocalChangeFinder:
    """Finds local entity changes that need syncing to Kanka."""
    
    def __init__(self, base_path: Path):
        self.base_path = base_path
        self.entities_path = base_path / "entities"
        self.new_entities: List[Dict] = []
        self.modified_entities: List[Dict] = []
        self.errors: List[Dict] = []
    
    def find_changes(self):
        """Scan for local changes."""
        print("Scanning for local entity changes...")
        
        for entity_dir in self.entities_path.iterdir():
            if not entity_dir.is_dir() or entity_dir.name.startswith("."):
                continue
            
            for file_path in entity_dir.glob("*.md"):
                # Skip conflict files
                if file_path.name.endswith((".local.md", ".kanka.md")):
                    continue
                
                self._check_entity(file_path)
        
        self._print_report()
    
    def _check_entity(self, file_path: Path):
        """Check if an entity needs to be pushed."""
        try:
            # Parse the file
            content = file_path.read_text(encoding="utf-8")
            
            if not content.startswith("---\n"):
                # No frontmatter, skip
                return
            
            parts = content.split("---\n", 2)
            if len(parts) < 3:
                return
            
            frontmatter = yaml.safe_load(parts[1]) or {}
            
            # Get entity name
            name = frontmatter.get("name", file_path.stem)
            
            # Check if it's a new entity
            if not frontmatter.get("entity_id"):
                self.new_entities.append({
                    "name": name,
                    "path": str(file_path.relative_to(self.base_path)),
                    "type": file_path.parent.name.rstrip("s")  # Remove plural
                })
                return
            
            # Check if it's modified
            if frontmatter.get("updated"):
                # Parse the updated timestamp
                updated_str = frontmatter["updated"]
                if updated_str.endswith("Z"):
                    updated_str = updated_str[:-1] + "+00:00"
                    
                try:
                    remote_updated = datetime.fromisoformat(updated_str).timestamp()
                    file_mtime = file_path.stat().st_mtime
                    
                    # If file was modified more than 60 seconds after last sync
                    if file_mtime > remote_updated + 60:
                        self.modified_entities.append({
                            "name": name,
                            "path": str(file_path.relative_to(self.base_path)),
                            "entity_id": frontmatter["entity_id"],
                            "last_sync": frontmatter["updated"],
                            "local_modified": datetime.fromtimestamp(file_mtime).isoformat()
                        })
                except Exception as e:
                    self.errors.append({
                        "path": str(file_path.relative_to(self.base_path)),
                        "error": f"Failed to parse timestamp: {e}"
                    })
                    
        except Exception as e:
            self.errors.append({
                "path": str(file_path.relative_to(self.base_path)),
                "error": str(e)
            })
    
    def _print_report(self):
        """Print a summary of local changes."""
        print("\n" + "="*60)
        print("LOCAL CHANGES REPORT")
        print("="*60)
        
        if self.new_entities:
            print(f"\n🆕 NEW ENTITIES ({len(self.new_entities)})")
            for entity in self.new_entities:
                print(f"  - {entity['name']} ({entity['type']}) -> {entity['path']}")
        
        if self.modified_entities:
            print(f"\n📝 MODIFIED ENTITIES ({len(self.modified_entities)})")
            for entity in self.modified_entities:
                print(f"  - {entity['name']} (ID: {entity['entity_id']})")
                print(f"    Path: {entity['path']}")
                print(f"    Last sync: {entity['last_sync']}")
                print(f"    Modified: {entity['local_modified']}")
        
        if not self.new_entities and not self.modified_entities:
            print("\n✓ No local changes to push")
        
        if self.errors:
            print(f"\n❌ ERRORS ({len(self.errors)})")
            for error in self.errors:
                print(f"  - {error['path']}: {error['error']}")
        
        print("\n" + "="*60)
        
        # Summary
        total_changes = len(self.new_entities) + len(self.modified_entities)
        if total_changes > 0:
            print(f"\nTotal changes to push: {total_changes}")
            print("\nNext step: Run push_to_kanka.py to sync these changes")


def main():
    """Main entry point."""
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    
    finder = LocalChangeFinder(project_root)
    finder.find_changes()


if __name__ == "__main__":
    main()