# Entity Sync Workflow

This document describes the workflow for syncing entities between Kanka and local markdown files.

## Overview

The sync workflow uses a hybrid approach:
- **Python scripts** handle deterministic tasks (fetching, comparing, categorizing)
- **LLM agent** handles intelligent tasks (resolving conflicts, merging content)

## Prerequisites

1. Install dependencies:
   ```bash
   pip install -r scripts/requirements.txt
   ```

2. Set environment variables:
   ```bash
   export KANKA_TOKEN='your-kanka-api-token'
   export KANKA_CAMPAIGN_ID='your-campaign-id'
   ```

## Pull Workflow (Kanka → Local)

### 1. Run the Pull Script

```bash
python scripts/pull_from_kanka.py
```

This script:
- Fetches all entities from Kanka with their posts (efficiently in one call per entity type)
- Compares with local files using timestamps
- Categorizes each entity as:
  - **New**: Exists in Kanka but not locally
  - **Updated**: Kanka version is newer
  - **Conflict**: Both local and Kanka have changes
  - **Deleted**: Exists locally but not in Kanka
  - **Unchanged**: No changes needed

### 2. Review the Pull Report

The script outputs a detailed report:

```
==============================================================
PULL REPORT
==============================================================

✅ NEW ENTITIES (3)
  - Gandalf (character) -> entities/characters/gandalf.md
  - Rivendell (location) -> entities/locations/rivendell.md
  - Fellowship (organization) -> entities/organizations/fellowship.md

📥 UPDATED FROM KANKA (2)
  - Frodo (character)
  - Shire (location)

⚠️  CONFLICTS (1)
  - Aragorn (character)
    Local: entities/characters/aragorn.local.md
    Kanka: entities/characters/aragorn.kanka.md

🗑️  DELETED FROM KANKA (1)
  - Old NPC -> entities/.deleted/20250106_143022_old-npc.md

✓ UNCHANGED (45)
  Including 3 with local changes only
```

### 3. Resolve Conflicts

For each conflict, the script creates two files:
- `.local.md` - Your local version
- `.kanka.md` - The Kanka version

To resolve conflicts, use the LLM agent:

```bash
# Command to be added to .claude/commands/
claude-code reconcile-conflicts
```

The LLM will:
1. Read both versions
2. Understand the semantic differences
3. Create a merged version preserving important changes from both
4. Update the main file and clean up conflict files

## Push Workflow (Local → Kanka)

### 1. Identify Changes to Push

```bash
python scripts/find_local_changes.py  # To be implemented
```

This will identify:
- New local entities (no entity_id in frontmatter)
- Modified local entities (file timestamp > frontmatter updated timestamp)

### 2. Push Changes

```bash
# Push specific files
python scripts/push_to_kanka.py entities/characters/gandalf.md entities/locations/rivendell.md

# Push all local changes (with confirmation prompt)
python scripts/push_to_kanka.py --all
```

This script will:
- Create new entities in Kanka
- Update existing entities
- Update frontmatter with new entity_ids and timestamps
- Set file modification times to match Kanka timestamps

## File Structure

### Entity Files

```yaml
---
entity_id: 12345
name: Aragorn
type: Player Character
tags: 
  - ranger
  - king
  - hero
is_hidden: false
created: 2024-01-15T10:30:00Z
updated: 2024-06-20T14:45:00Z
---

# Aragorn

Heir of Isildur and rightful king of Gondor...
```

### Post Files

Posts are stored in subdirectories:
```
entities/characters/aragorn.md
entities/characters/aragorn/
  ├── secret-lineage.md
  └── sword-of-elendil.md
```

Post frontmatter:
```yaml
---
post_id: 67890
entity_id: 12345
title: Secret Lineage
is_hidden: true
created: 2024-02-10T09:00:00Z
---
```

## Conflict Resolution Details

### How Conflicts Are Detected

The pull script uses timestamps to detect conflicts:

1. **Remote Update Time**: From Kanka's `updated_at` field
2. **Last Known Remote Time**: Stored in local frontmatter `updated` field
3. **Local File Time**: File system modification time

A conflict occurs when:
- Remote has been updated since last pull (remote_updated > last_known_remote)
- AND local file has been modified (file_mtime > last_known_remote + buffer)

### Manual Conflict Resolution

If you prefer to resolve conflicts manually:

1. Compare the files:
   ```bash
   diff entities/characters/aragorn.local.md entities/characters/aragorn.kanka.md
   ```

2. Edit the main file with your merged content:
   ```bash
   vim entities/characters/aragorn.md
   ```

3. Clean up conflict files:
   ```bash
   rm entities/characters/aragorn.local.md entities/characters/aragorn.kanka.md
   ```

## Best Practices

### 1. Regular Pulls
- Pull from Kanka before making local changes
- This minimizes conflicts

### 2. Atomic Changes
- Make focused changes to individual entities
- Commit changes to git after resolving conflicts

### 3. Use Tags
- Tag entities in Kanka for easier filtering
- Local tag changes sync bidirectionally

### 4. Private Content
- Use `is_hidden: true` for GM-only content
- Private posts stay in their subdirectories

### 5. Backup
- The `.deleted/` folder preserves deleted entities
- Use git to track all changes
- Conflict files (.local.md, .kanka.md) are preserved until manually resolved

## Troubleshooting

### Missing Entity IDs
If an entity exists locally but has no `entity_id` in frontmatter:
- It's treated as a new entity for pushing
- Run push script to create it in Kanka
- The script will update the frontmatter with the new ID

### Timestamp Issues
If timestamps seem wrong:
- Check your system timezone
- Kanka uses UTC timestamps
- File modification times use local timezone

### API Rate Limits
The scripts respect Kanka's rate limits:
- Fetches all entities of a type in one call
- Uses batch operations where possible
- Includes automatic retry logic

### Large Campaigns
For campaigns with many entities:
- The pull script shows progress as it fetches each entity type
- Conflicts are handled one at a time
- Use filtering options (to be implemented) to sync subsets

## Future Enhancements

1. **Selective Sync**
   - Filter by entity type
   - Filter by tags
   - Filter by date range

2. **Dry Run Mode**
   - Preview what would change
   - No actual modifications

3. **Automated Backups**
   - Archive before major syncs
   - Configurable retention

4. **Webhook Integration**
   - Real-time sync when Kanka entities change
   - Requires Kanka subscription