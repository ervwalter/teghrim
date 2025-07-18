# CLAUDE.md

This file provides conceptual guidance for understanding the Teghrim campaign management system.

## Project Overview

This is an AI-powered RPG campaign management system that transforms tabletop game sessions into structured knowledge. The core concept is maintaining a living campaign database that grows with each session while preserving the full history of how the world and characters evolve.

**Campaign Setting**: This is a Pathfinder 2e Remastered campaign with a homebrew world called Septerra. Understanding PF2e mechanics helps interpret game terms in transcripts and digests (e.g., "slayer", "hero points", "dying condition", "flanking").

## Core Concepts

### The Knowledge Pipeline
Audio recordings of game sessions flow through multiple transformation stages:
- **Transcripts**: Raw timestamped dialogue from sessions
- **Digests**: Structured extracts of all game-relevant events, organized chronologically with tagged entries
- **Entity Files**: Living documents for characters, locations, organizations, etc. that accumulate history
- **Session Summaries**: Narrative retellings suitable for players to review between sessions

### Entity-Centric Design
Everything revolves around entities - the people, places, and things that make up the campaign world. Each entity:
- Lives as a markdown file with YAML frontmatter
- Accumulates history over time (never delete, only add)
- Links to other entities using Kanka's `[entity:ID|display text]` syntax
- Syncs bidirectionally with Kanka.io for online campaign management

## Entity Management Philosophy

### Local Files as Source of Truth
The `entities/` directory contains the authoritative version of all campaign content:
- Organized by type: `characters/`, `locations/`, `organizations/`, etc.
- Each entity is a markdown file with YAML frontmatter
- Files use kebab-case naming: `bruldin-grimstone.md`
- Bidirectional sync with Kanka maintains consistency

### Entity File Structure
```yaml
---
name: Entity Name
entity_id: 1234567  # Kanka ID, absent for new entities
type: Specific Type  # e.g., "City", "Deity", "Player Character"
tags: ["tag1", "tag2"]  # From controlled vocabulary
is_hidden: false  # true = GM only
created: '2025-01-01T00:00:00+00:00'
updated: '2025-01-01T00:00:00+00:00'
---

# Entity Name

Current state summary - the "evergreen" description that captures their current state and significance in the campaign world.

## Description  
Physical appearance, personality, defining characteristics

## Notable History
- **Event Name**: What happened and when
- **Another Event**: More history (chronological order)

## Current Status
Where they are now and what they're doing

## Secrets & Mysteries
GM-only information if is_hidden: true
```

**Quest-specific structure**:
```yaml
---
name: Quest Name
entity_id: 1234567
type: Party Quest  # or "Personal Quest", "Combat"
is_hidden: false
is_completed: false  # true when quest is complete
created: '2025-01-01T00:00:00+00:00'
updated: '2025-01-01T00:00:00+00:00'
---
```

### Entity Types and Tags
- **ALWAYS read metadata.json first** before creating or updating any entity
- Use only types and tags defined in metadata.json for that entity type
- If a new type or tag seems necessary, suggest it but wait for user confirmation before using
- metadata.json is the authoritative source for controlled vocabulary

### Writing Principles
- **Wikipedia-style**: In-world perspective, no meta-game references
- **No Overview heading**: The lead paragraph appears directly after the title (like Wikipedia)
- **Accumulative**: Never delete content, only add new information
- **Evergreen lead**: Keep the opening paragraph current with the entity's present state
- **Chronological History**: Add events as they happen
- **Cross-linked**: Use `[entity:ID|display text]` to connect entities

### Entity Linking Rules
- Link first mention of each entity **per paragraph**
- Use natural display text: `[entity:7763290|the Norn wanderer]`
- Entity IDs found in frontmatter or via `scripts/get_entity_overview.py`

### Special Entity Types

**Digests** (`entities/notes/digest-YYYY-MM-DD.md`):
- Structured extraction from session transcripts
- Tagged chronological events (SCENE, ACTION, DIALOGUE, COMBAT, etc.)
- Source material for entity updates and session summaries
- **IMPORTANT**: Digests should NEVER contain entity links - they are raw source material

**Session Summaries** (`entities/journals/session-summary-YYYY-MM-DD.md`):
- Narrative retellings of game sessions
- Player-facing documents
- Generated from digests with entity context
- Should include entity links to relevant quests in quest update sections

**Session Narratives** (`entities/journals/session-narrative-YYYY-MM-DD.md`):
- Literary retellings of game sessions
- Focus on narrative flow and storytelling
- Entity links should be used sparingly and ONLY where they enhance rather than disrupt the narrative
- Quest links are appropriate when quests are explicitly mentioned in dialogue or pivotal moments

**Player Characters**:
- Tracked in `entities/notes/players.md` for player-to-character mapping
- Special handling in overview scripts

## Temporal Considerations

When working with campaign content, remember:
- Entity files show the "current" state with full history
- Digests capture what happened in a specific session
- Session summaries should only include information known at that point in time
- Never include future events when processing historical sessions

## The Sync Philosophy

Local files and Kanka work together:
- Local: Fast editing, version control, bulk operations
- Kanka: Online access, player viewing, relationship visualization
- Conflicts resolved intelligently, preserving content from both sources
- Entity IDs connect the two systems

## Quest Management Guidelines

### Quest Creation
When creating quests from session content:
- Check existing quests to avoid duplication
- Include all participants who were actually present (verify against digests/summaries)
- Create quests for all major events, not just explicitly named missions

### Quest Linking
Add quest entity links in appropriate places:
- **Session Summaries**: Link quests in the Quest Updates section
- **Session Narratives**: Only link quests where naturally mentioned in narrative flow
- **Character Files**: Link quests in Notable History or Current Status sections
- **Location/Organization Files**: Link relevant quests in history entries
- **Quest Files**: Add "Related Quests" sections for interconnected storylines
- **Creature Files**: Link quests where creatures play significant roles

### Quest Completion Status
- **DO NOT use tags** to track quest status (no "active" or "completed" tags)
- Use the native `is_completed` boolean field in quest frontmatter:
  - `is_completed: false` for active/ongoing quests
  - `is_completed: true` for completed quests
- This field syncs with Kanka's native quest completion tracking
- When updating quest status, only change the `is_completed` field

### Common Corrections
- Hobs ≠ Hobgoblins (hobs are domesticated goblins, hobgoblins are a larger goblinoid race)
- Verify participant lists against actual session attendance
- The Goblin King is a goblin, not a hobgoblin

## Using Chunkhound Semantic Search

The chunkhound MCP server provides powerful semantic search capabilities for finding relevant content across the codebase. Use it effectively by:

### Path Filtering Issue
**IMPORTANT**: The `path` parameter is currently non-functional in chunkhound. Path filtering returns no results regardless of the path format used. Until this is fixed, use the workarounds below.

### Workaround Search Patterns
Since path filtering doesn't work, use these strategies:

1. **Character Research**: Search with character name + key traits
   - Example: `"Bruldin dwarf slayer scars battle"`
   - Manually filter results by checking `file_path` field for `entities/characters/`

2. **Location Context**: Search with location name + notable features
   - Example: `"Teghrim's Crossing bridge settlement trade"`
   - Look for results with `file_path` containing `entities/locations/`

3. **Quest Tracking**: Search for quest events or participants
   - Example: `"wagon recovery goblin attack"`
   - Filter for `file_path` containing `entities/quests/`

4. **Cross-Entity Connections**: Search broadly without path restrictions
   - Review all results and identify relevant files by their paths
   - Use specific search terms to reduce noise

5. **Session Processing**: When updating entities from new sessions
   - Search without path restrictions for existing entity content
   - Use character names, location names, and key events as search terms
   - Verify entity IDs and existing history before making changes
   - Manually check `file_path` to ensure you're looking at entity files

### Performance Tips
- Use smaller `page_size` (3-5) for initial searches to manage noise
- Increase `page_size` when you need comprehensive results
- Since you can't filter by path, use more specific search terms
- The similarity threshold can help filter results, but start without it
- Total results count helps gauge if your search is too broad or narrow

### Required Parameters
**IMPORTANT**: When using chunkhound semantic search, you MUST always specify:
- `model`: Always use `"snowflake-arctic-embed2"`
- `provider`: Always use `"openai-compatible"`

Without these parameters, chunkhound will return no search results.

## Combat Mini Color Coding System

**IMPORTANT**: During live gameplay, enemies are distinguished using colored miniatures on the table (red orc, blue goblin, etc.). These color designations are **out-of-game table management only** and should NEVER appear in:

- Session summaries
- Session narratives  
- Entity files
- Any player-facing content

### Digest Processing
- Digests may retain color coding for accuracy in capturing raw transcript content
- When creating summaries/narratives from digests, convert colors to:
  - Generic descriptions: "the lead orc", "another goblin", "the wounded enemy"
  - Positional references: "the orc near the fence", "the goblin behind cover"
  - Distinguishing features: "the larger orc", "the archer", "the mounted goblin"
  - Sequential numbering if needed: "first orc eliminated", "second wave of attackers"

### Example Conversions
- "red orc #2" → "the orc leader" or "another orc warrior"
- "blue goblin archers" → "goblin archers" or "the mounted goblins"
- "green scarecrow" → "the scarecrow" or "another straw construct"

This maintains narrative immersion while preserving the tactical clarity needed for digest accuracy.