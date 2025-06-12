# Campaign Reset Workflow

This document describes how to handle scenarios where the Kanka campaign has been reset or cleared.

## When to Use This Workflow

Use these special flags when:
- The Kanka campaign has been completely reset/cleared
- All entity IDs in Kanka are now invalid
- You want to preserve local entities and repush everything fresh

## Commands

### 1. Pull Without Deleting Local Entities

When the campaign has been cleared, use the `--preserve-local` flag to prevent deletion of entities that are missing from Kanka:

```bash
python scripts/pull_from_kanka.py --preserve-local
```

This will:
- Pull any new entities from Kanka (if any)
- Update existing entities that match by name
- **Preserve** local entities that are missing from Kanka (instead of moving them to `.deleted`)
- Report preserved entities in the summary

### 2. Force Repush All Entities

To recreate all entities in Kanka with new IDs, use the `--force-repush` flag:

```bash
# Force repush specific entities
python scripts/push_to_kanka.py --force-repush entities/characters/moradin.md

# Force repush ALL entities (requires confirmation)
python scripts/push_to_kanka.py --all --force-repush
```

This will:
- Ignore existing `entity_id` values in frontmatter
- Create all entities as new in Kanka
- Update local files with the new entity IDs
- Recreate all posts with new IDs

## Complete Reset Workflow

1. **Backup your local entities** (optional but recommended):
   ```bash
   cp -r entities/ entities.backup/
   ```

2. **Pull from empty Kanka** (preserving local entities):
   ```bash
   python scripts/pull_from_kanka.py --preserve-local
   ```

3. **Force repush all entities**:
   ```bash
   python scripts/push_to_kanka.py --all --force-repush
   ```

4. **Verify the upload**:
   ```bash
   python scripts/pull_from_kanka.py
   ```

## Important Notes

- The `--force-repush` flag will create duplicate entities if the campaign hasn't been cleared
- Always use `--preserve-local` when pulling from a cleared campaign
- Entity IDs will change during force repush - any external references will need updating
- Posts are also recreated with new IDs during force repush