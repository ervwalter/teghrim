# Transcript to Digest Processing

## Purpose

Transform verbose, raw transcripts into structured session digests that capture all game-relevant information while removing speech artifacts and organizing content chronologically.

## Input

- **Source**: Raw transcript files from audio transcription
- **Format**: Timestamped speaker dialogue with all speech preserved
- **Length**: Typically 50-150 pages of raw text per session

## Process

### 1. Content Segmentation

The transcript is divided into logical segments based on:
- **Scene Changes**: Travel, location shifts, time jumps
- **Encounter Boundaries**: Combat start/end, NPC meetings
- **Activity Types**: Roleplay, combat, exploration, downtime
- **Natural Breaks**: Long pauses, session breaks

### 2. Entity Recognition

Each segment is analyzed to identify:
- **Characters**: PCs, NPCs, mentioned individuals
- **Locations**: Cities, buildings, regions, landmarks  
- **Organizations**: Guilds, governments, groups
- **Items**: Equipment, artifacts, treasure
- **Events**: Battles, meetings, discoveries
- **Game Terms**: Spells, abilities, conditions

New entities are marked with "(？)" for later validation.

### 3. Speech Cleanup

Transform natural speech into clean text:
- Remove filler words ("um", "uh", "like")
- Consolidate repeated phrases
- Fix false starts and corrections
- Merge interrupted sentences
- Preserve essential dialogue and descriptions

### 4. Information Structuring

Organize content by type:
- **SCENE**: Location changes, time transitions
- **RP**: Character dialogue and interactions
- **COMBAT**: Battle sequences with outcomes
- **DISCOVERY**: Lore, clues, revelations
- **DECISION**: Party choices and consequences
- **LOOT**: Items gained or lost
- **ROLL**: Significant skill checks and results

### 5. Chronological Assembly

Events are ordered to create a clear narrative flow:
- Maintain temporal sequence
- Group related actions together
- Insert time markers where known
- Flag flashbacks or visions

## Output Format

```markdown
# Session Digest - YYYY-MM-DD

## Chronological Log

1. SCENE – The party arrives at Teghrim's Crossing, a bridge spanning the Rothehurst River, with hostels, stores, and dining areas under the command of Captain Irka Spritzel (？). Irka assigns the party tasks in return for accommodations.

2. RP – The party meets Alrik Grimmelstang (Cleric, Dwarf, PC), who discusses his past, his secretive recipe, and paranoia regarding Fey.

3. COMBAT – Fight with 6 skims (？) at the old mansion:
   - Round 1: Aurelia sneaks ahead, spots enemies
   - Round 2-3: Ranged exchanges, Alrik casts Divine Lance
   - Round 4-5: Melee engagement, necromancer flees
   - Outcome: Victory, all enemies defeated

4. DISCOVERY – The mansion's new owner is revealed as Osanna Von Carstein (？), a vampire noble from one of the three great vampire houses.

5. LOOT – Party receives:
   - Cold iron rapier
   - Fanged dagger (magical, rune inscribed)
   - 10 gold per person from Osanna
```

## Quality Standards

### Must Preserve
- All character names (even if misspelled)
- Exact locations visited
- Combat outcomes and casualties
- Items gained or lost
- Plot revelations
- Party decisions
- NPC relationships formed

### May Condense
- Repetitive actions
- Table talk and rules discussions
- Multiple attempts at same action
- Extended descriptions
- Combat blow-by-blow (keep key moments)

### Must Remove
- Player out-of-character planning
- Rules arguments
- Real-world references
- Technical difficulties
- Bathroom breaks

## Entity Validation

New entities marked with "(？)" require:
- Consistent spelling throughout digest
- Appropriate categorization
- Context for first appearance
- Relationships to other entities

## Session Metadata

Each digest includes:
- Session date (real world)
- In-game date if mentioned
- Location progression
- Major accomplishments
- Cliffhanger or next goals

## Collaborative Review

After AI processing, digests enter review phase:
- Players correct entity names
- GM verifies plot details  
- Misattributed actions are fixed
- Missing context is added
- (？) markers are resolved

## Next Stage

The detailed digest serves as the authoritative session record. From this, more focused outputs are generated: summaries for quick reference and narratives for immersive reading.