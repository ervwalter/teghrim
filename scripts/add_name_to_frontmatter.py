#!/usr/bin/env python3
"""
Add name property to entity frontmatter by extracting from content.
"""

import re
from pathlib import Path
import yaml


def extract_name_from_content(content: str) -> str:
    """Extract the entity name from the markdown content."""
    # Look for the first # heading after the frontmatter
    lines = content.split('\n')
    
    # Skip past frontmatter
    past_frontmatter = False
    dash_count = 0
    
    for line in lines:
        if line.strip() == '---':
            dash_count += 1
            if dash_count == 2:
                past_frontmatter = True
            continue
        
        # Look for first heading after frontmatter
        if past_frontmatter and line.startswith('# '):
            return line[2:].strip()
    
    return None


def add_name_to_file(file_path: Path):
    """Add name property to a single file's frontmatter."""
    try:
        content = file_path.read_text(encoding='utf-8')
        
        if not content.startswith('---\n'):
            print(f"Skipping {file_path}: No frontmatter found")
            return
        
        # Split frontmatter and content
        parts = content.split('---\n', 2)
        if len(parts) < 3:
            print(f"Skipping {file_path}: Invalid frontmatter format")
            return
        
        # Parse frontmatter
        frontmatter = yaml.safe_load(parts[1]) or {}
        
        # Skip if already has name
        if 'name' in frontmatter:
            print(f"Skipping {file_path}: Already has name: {frontmatter['name']}")
            return
        
        # Extract name from content
        full_content = '---\n' + parts[1] + '---\n' + parts[2]
        name = extract_name_from_content(full_content)
        
        if not name:
            print(f"Warning: Could not extract name from {file_path}")
            return
        
        # Add name to frontmatter
        frontmatter['name'] = name
        
        # Reconstruct file with name as first property
        new_content = "---\n"
        # Put name first
        new_content += f"name: {name}\n"
        # Then other properties
        for key, value in frontmatter.items():
            if key != 'name':
                if isinstance(value, list):
                    new_content += f"{key}: {value}\n"
                else:
                    new_content += f"{key}: {value}\n"
        new_content += "---\n"
        new_content += parts[2]
        
        # Write back
        file_path.write_text(new_content, encoding='utf-8')
        print(f"Updated {file_path.parent.name}/{file_path.name}: {name}")
        
    except Exception as e:
        print(f"Error processing {file_path}: {e}")


def main():
    """Process all entity files."""
    script_dir = Path(__file__).parent
    entities_dir = script_dir.parent / "entities"
    
    if not entities_dir.exists():
        print(f"Error: {entities_dir} does not exist")
        return
    
    # Process all .md files in entities subdirectories
    total = 0
    for subdir in entities_dir.iterdir():
        if subdir.is_dir():
            for md_file in subdir.glob("*.md"):
                add_name_to_file(md_file)
                total += 1
    
    print(f"\nProcessed {total} files")


if __name__ == "__main__":
    main()