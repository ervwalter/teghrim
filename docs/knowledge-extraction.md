# Entity Extraction from Digests

## Purpose

Extract entity information from session digests to update the local markdown entity files that sync with Kanka. This process identifies new entities, updates existing ones with session events, and maintains the interconnected web of campaign knowledge.

## Input

- **Primary**: Finalized session digests with resolved entity names
- **Context**: Existing campaign knowledge base
- **Temporal**: Session date for chronological tracking

## Process

### 1. Entity Identification

Scan the digest for all mentioned entities and match them to existing files or flag as new:

**Characters**
- Player Characters (PCs)
- Non-Player Characters (NPCs)
- Mentioned individuals
- Deceased characters

**Locations**
- Settlements (cities, towns, villages)
- Buildings (taverns, shops, temples)
- Regions (kingdoms, provinces)
- Geographic features (rivers, mountains)

**Organizations**
- Formal groups (guilds, governments)
- Informal alliances
- Religious orders
- Criminal networks

**Items**
- Equipment and weapons
- Magical artifacts
- Trade goods
- Plot-relevant objects

**Events**
- Battles and conflicts
- Political changes
- Natural disasters
- Prophecies and omens

### 2. Information Extraction

For each entity mentioned in the digest, extract:

**New Entity Information**
- Name and any aliases used
- Entity type (character, location, organization, etc.)
- Initial description from context
- Type field (NPC, City, Deity, etc.)
- Tags based on context

**Type-Specific Details**

*Characters*:
- Race/ancestry
- Class/profession
- Affiliations
- Notable abilities
- Relationships
- Motivations

*Locations*:
- Parent location
- Population
- Government type
- Notable features
- Important residents
- Economic focus

*Organizations*:
- Leadership structure
- Members
- Goals/purpose
- Resources
- Territories
- Rivals/allies

*Items*:
- Current owner
- Previous owners
- Magical properties
- Value/rarity
- Origin/creator
- Plot significance

### 3. Entity File Updates

For existing entities:
- Add new events to "Notable History" section
- Update "Current Status" if changed
- Add new relationships or affiliations
- Update location if moved
- Note any status changes (alive → dead)

For new entities:
- Create file in appropriate directory
- Use kebab-case naming
- Include YAML frontmatter (no entity_id yet)
- Write initial sections based on digest info

### 4. Entity Linking

Add cross-references between entities:
- Use `[entity:ID|display text]` syntax
- Link first mention per paragraph
- Find entity IDs via `get_entity_overview.py`
- Use descriptive display text

### 5. Special Entity Types

**Session Digests** (`entities/notes/digest-YYYY-MM-DD.md`):
- Already created during digest phase
- Source of truth for session events
- Tagged with "Session Digest"

**Player Notes** (`entities/notes/players.md`):
- Update player-to-character mappings
- Track character status changes
- Note new player characters

## Output Examples

### New Character Entity
```yaml
---
name: Osanna Von Carstein
type: Vampire Noble
tags:
  - vampire
  - noble
  - npc
is_hidden: false
created: '2025-05-30T10:00:00+00:00'
updated: '2025-05-30T10:00:00+00:00'
---

# Osanna Von Carstein

## Overview
A vampire noble of House Von Carstein who recently acquired property near [entity:7763291|Teghrim's Crossing].

## Description
Elegant and dangerous, with the bearing of ancient nobility and crimson eyes that betray her vampiric nature.

## Notable History
- **Mansion Acquisition (2025-05-30)**: Hired the party to clear her new property of skims, then gifted them the mansion as payment

## Current Status
Residing in the main house near the old mansion, establishing her presence in the Teghrim's Crossing area.
```

### Updated Location Entity
```markdown
## Notable History
- **Bridge Construction**: Built 200 years ago to span the Rothehurst River
- **Vampire Neighbor (2025-05-30)**: [entity:8234567|Osanna Von Carstein] established residence nearby
```

## Quality Standards

### Entity File Requirements
- Names must match digest spelling exactly
- Use controlled vocabulary tags from metadata.json
- Maintain Wikipedia-style in-world perspective
- Never delete existing content, only add
- Keep Overview sections evergreen
- Add events chronologically to Notable History

### Linking Requirements
- Verify entity IDs before linking
- Use natural display text
- Link first mention per paragraph
- Check links resolve correctly

## Workflow Integration

### Entity Creation Process
1. Check if entity file already exists
2. Determine appropriate entity type and directory
3. Create file with kebab-case name
4. Add frontmatter (no entity_id yet)
5. Write initial content from digest
6. Will get entity_id on first push to Kanka

### Entity Update Process
1. Open existing entity file
2. Add new events to Notable History with date
3. Update Current Status if changed
4. Add new relationships/affiliations
5. Update frontmatter 'updated' timestamp
6. Preserve all existing content

## Common Patterns

### From Digest Entry to Entity Update

**Digest**: "DISCOVERY – The mansion's new owner is revealed as Osanna Von Carstein, a vampire noble"

**New Entity**: Create `entities/characters/osanna-von-carstein.md`

**Location Update**: Add to `entities/locations/old-mansion.md`:
```markdown
## Notable History
- **New Ownership (2025-05-30)**: Acquired by [entity:8234567|Osanna Von Carstein]
```

## File Organization

```
entities/
├── characters/         # PCs, NPCs, deities
├── locations/          # Places, regions, buildings
├── organizations/      # Groups, factions, guilds
├── creatures/          # Monster types (not individuals)
├── races/              # Ancestries and cultures
├── quests/             # Missions and objectives
├── notes/              # Digests, GM notes, player info
└── journals/           # Session summaries
```

## Usage with Tools

### Finding Entity IDs for Linking
```bash
python scripts/get_entity_overview.py
```

### After Extraction
```bash
# Check what needs syncing
python scripts/find_local_changes.py

# Push new/updated entities to Kanka
python scripts/push_to_kanka.py --all
```

## Success Metrics

Effective entity extraction results in:
- All digest entities captured in files
- Consistent naming across all references
- Rich interconnected entity web
- Complete session history preserved
- Easy navigation via entity links
- Seamless Kanka synchronization

## Next Stage

Extracted entities sync to Kanka via push scripts, making them available in the online campaign. Session summaries can then be generated with proper entity links for player reference.