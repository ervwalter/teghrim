#!/usr/bin/env python3
"""
Clean all entities from the Kanka campaign.

WARNING: This will permanently delete ALL entities in your campaign!
Use with extreme caution.
"""

import asyncio
import os
from pathlib import Path
from typing import Any, Dict, List

from mcp_kanka import KankaOperations, create_operations


def confirm_action(campaign_id: str) -> bool:
    """Ask for user confirmation before proceeding."""
    print("\n" + "="*60)
    print("⚠️  WARNING: CAMPAIGN CLEANUP ⚠️")
    print("="*60)
    print(f"\nThis will PERMANENTLY DELETE ALL entities in campaign {campaign_id}!")
    print("This action cannot be undone.")
    print("\nAffected entity types:")
    print("  - Characters")
    print("  - Locations")
    print("  - Organizations")
    print("  - Races")
    print("  - Creatures")
    print("  - Notes")
    print("  - Journals")
    print("  - Quests")
    
    print("\n" + "="*60)
    response = input("Type 'DELETE EVERYTHING' to proceed, or anything else to cancel: ")
    
    return response == "DELETE EVERYTHING"


async def clean_campaign():
    """Remove all entities from the campaign."""
    campaign_id = os.environ.get("KANKA_CAMPAIGN_ID")
    
    if not campaign_id:
        print("Error: KANKA_CAMPAIGN_ID must be set")
        return

    # Ask for confirmation
    if not confirm_action(campaign_id):
        print("\nCancelled. No entities were deleted.")
        return

    print(f"\nStarting cleanup of campaign {campaign_id}...")
    
    # Create operations instance
    operations = create_operations()
    
    # Entity types to clean
    entity_types = [
        "journal",  # Clean these first as they might have posts
        "quest",
        "note",
        "character",
        "creature", 
        "location",
        "organization",
        "race",
    ]
    
    total_deleted = 0
    total_errors = 0

    for entity_type in entity_types:
        print(f"\nFetching all {entity_type}s...")
        
        try:
            # Fetch all entities of this type
            result = await operations.find_entities(
                entity_type=entity_type,
                limit=0  # Get all
            )
            
            entities = result.get("entities", [])
            if not entities:
                print(f"  No {entity_type}s found")
                continue
                
            print(f"  Found {len(entities)} {entity_type}s to delete")
            
            # Collect entity IDs
            entity_ids = [entity["entity_id"] for entity in entities]
            
            # Delete in batches
            batch_size = 10
            for i in range(0, len(entity_ids), batch_size):
                batch_ids = entity_ids[i:i + batch_size]
                print(f"  Deleting batch {i//batch_size + 1}/{(len(entity_ids) + batch_size - 1)//batch_size}...")
                
                delete_result = await operations.delete_entities(batch_ids)
                
                # Count successes and errors
                for item in delete_result:
                    if item.get("success"):
                        total_deleted += 1
                    else:
                        total_errors += 1
                        print(f"    Failed to delete entity {item.get('entity_id', 'unknown')}: {item.get('error', 'Unknown error')}")
            
            print(f"  ✓ Deleted {len([r for r in delete_result if r.get('success')])} {entity_type}s")
            
        except Exception as e:
            print(f"  Error processing {entity_type}s: {e}")
            total_errors += 1

    print("\n" + "="*60)
    print(f"Campaign cleanup complete!")
    print(f"Total entities deleted: {total_deleted}")
    if total_errors > 0:
        print(f"Total errors: {total_errors}")
    print("="*60)
    
    if total_deleted > 0:
        print("\nNext steps:")
        print("1. Pull from the empty campaign:")
        print("   python scripts/pull_from_kanka.py --preserve-local")
        print("\n2. Force repush all local entities:")
        print("   python scripts/push_to_kanka.py --all --force-repush")


async def main():
    """Main entry point."""
    # Check for required environment variables
    token = os.environ.get("KANKA_TOKEN")
    campaign_id = os.environ.get("KANKA_CAMPAIGN_ID")
    
    if not token or not campaign_id:
        print("Error: KANKA_TOKEN and KANKA_CAMPAIGN_ID must be set")
        print("\nExample:")
        print("  export KANKA_TOKEN='your-token-here'")
        print("  export KANKA_CAMPAIGN_ID='your-campaign-id'")
        print("  python scripts/clean_campaign.py")
        return
    
    await clean_campaign()


if __name__ == "__main__":
    asyncio.run(main())