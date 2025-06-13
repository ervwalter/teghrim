#!/usr/bin/env python3
"""
Generate a quick overview of all entities in the campaign, including frontmatter and first paragraph.
Includes resolved player information for easy reference.
"""

import os
import yaml
import re
from pathlib import Path
from typing import Dict, List, Optional

def extract_frontmatter_and_content(file_path: Path) -> tuple[dict, str]:
    """Extract YAML frontmatter and first content paragraph from a markdown file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Extract frontmatter
    if content.startswith('---'):
        try:
            _, fm, rest = content.split('---', 2)
            frontmatter = yaml.safe_load(fm)
            
            # Get first paragraph of content (skip empty lines and headers)
            lines = rest.strip().split('\n')
            first_para = []
            in_paragraph = False
            
            for line in lines:
                line = line.strip()
                if not line:
                    if in_paragraph:
                        break
                    continue
                if line.startswith('#'):
                    continue
                # Remove markdown formatting
                line = line.replace('**', '').replace('*', '').replace('`', '')
                in_paragraph = True
                first_para.append(line)
                if len(' '.join(first_para)) > 150:  # Limit to ~150 chars
                    break
            
            return frontmatter or {}, ' '.join(first_para)
        except:
            return {}, ""
    return {}, ""

def get_player_mappings(entities_dir: Path) -> tuple[Dict[int, Dict[str, str]], str]:
    """Extract player to character mappings and full content from players.md file."""
    players_file = entities_dir / "notes" / "players.md"
    mappings = {}
    full_content = ""
    
    if players_file.exists():
        with open(players_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split to get just the content after frontmatter
        if '---' in content:
            parts = content.split('---', 2)
            if len(parts) >= 3:
                full_content = parts[2].strip()
        
        # Extract character references - updated pattern to handle optional names
        pattern = r'(\w+) is a player who plays \[character:(\d+)(?:\|([^\]]+))?\]'
        matches = re.findall(pattern, content)
        
        for player_name, entity_id, char_name in matches:
            mappings[int(entity_id)] = {'player': player_name, 'character_name': char_name or ''}
    
    return mappings, full_content

def resolve_player_characters(entities: List[Dict], player_mappings: Dict[int, Dict[str, str]]) -> None:
    """Add player names to character entities based on mappings."""
    for entity in entities:
        if entity.get('entity_id') in player_mappings:
            entity['player_name'] = player_mappings[entity['entity_id']]['player']

def get_entities_overview(entities_dir: Path, entity_types: List[str]) -> Dict[str, List[Dict]]:
    """Get overview of specified entity types."""
    overview = {entity_type: [] for entity_type in entity_types}
    
    for entity_type in entity_types:
        type_dir = entities_dir / entity_type
        if not type_dir.exists():
            continue
            
        for file_path in sorted(type_dir.glob("*.md")):
            # Skip player notes and other special files
            if file_path.name == "players.md":
                continue
                
            frontmatter, first_para = extract_frontmatter_and_content(file_path)
            
            entity_info = {
                'file': f"{entity_type}/{file_path.name}",
                'name': frontmatter.get('name', file_path.stem),
                'type': frontmatter.get('type', ''),
                'entity_id': frontmatter.get('entity_id'),
                'tags': frontmatter.get('tags', []),
                'is_hidden': frontmatter.get('is_hidden', False),
                'summary': first_para[:150] + '...' if len(first_para) > 150 else first_para
            }
            
            overview[entity_type].append(entity_info)
    
    return overview

def format_overview(overview: Dict[str, List[Dict]], player_mappings: Dict[int, Dict[str, str]], players_content: str) -> str:
    """Format the overview into a readable summary."""
    output = ["# Entity Overview\n"]
    
    # First show the full players note content with resolved entity references
    if players_content:
        output.append("## Players")
        
        # Resolve entity references in the content
        resolved_content = players_content
        for entity_id, info in player_mappings.items():
            # Find the character in our overview to get the file path
            for entity in overview.get('characters', []):
                if entity.get('entity_id') == entity_id:
                    char_name = entity['name']
                    char_file = f"entities/{entity['file']}"
                    # Replace the entity reference with name and file path
                    old_ref = f"[character:{entity_id}|{char_name}]"
                    new_ref = f"{char_name} ({char_file})"
                    resolved_content = resolved_content.replace(old_ref, new_ref)
                    # Also handle case where name wasn't in the original
                    old_ref_no_name = f"[character:{entity_id}]"
                    if old_ref_no_name in resolved_content:
                        resolved_content = resolved_content.replace(old_ref_no_name, new_ref)
                    break
        
        output.append(resolved_content)
        output.append("")
    
    # Then show each entity type
    for entity_type, entities in overview.items():
        if not entities:
            continue
            
        output.append(f"## {entity_type.title()}")
        
        for entity in sorted(entities, key=lambda x: x['name']):
            # Format the entity line
            line = f"{entity['name']}"
            
            # Add entity ID if present
            if entity.get('entity_id'):
                line += f" [ID: {entity['entity_id']}]"
            
            # Add type if present
            if entity['type']:
                line += f" ({entity['type']})"
            
            # Add file path
            line += f" - entities/{entity['file']}"
            
            # Add tags if any
            if entity['tags']:
                line += f" [{', '.join(entity['tags'])}]"
            
            # Add summary on next line if present
            if entity['summary']:
                line += f"\n  {entity['summary']}"
            
            output.append(line)
        
        output.append("")
    
    # Add entity counts
    output.append("## Summary")
    total = 0
    for entity_type, entities in overview.items():
        if entities:
            count = len(entities)
            total += count
            output.append(f"{entity_type}: {count}")
    output.append(f"Total: {total} entities")
    
    return '\n'.join(output)

def main():
    """Main entry point."""
    # Determine project root
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    entities_dir = project_root / "entities"
    
    if not entities_dir.exists():
        print("Error: entities/ directory not found")
        return
    
    # Entity types to include in overview
    entity_types = ['notes', 'characters', 'locations', 'organizations', 'races', 'creatures', 'quests']
    
    # Get player mappings and content first
    player_mappings, players_content = get_player_mappings(entities_dir)
    
    # Get entity overview
    overview = get_entities_overview(entities_dir, entity_types)
    
    # Add player info to characters
    if 'characters' in overview:
        resolve_player_characters(overview['characters'], player_mappings)
    
    # Format and output
    formatted = format_overview(overview, player_mappings, players_content)
    print(formatted)

if __name__ == "__main__":
    main()