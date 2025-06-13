# Generate Session Summaries

This command creates session summaries as local journal entries for all digests that don't already have summaries.

## Usage

Run this command to automatically generate session summaries for any digests that are missing them. The summaries will be created locally and can be pushed to Kanka using the push-to-kanka command.

## Process

1. Find all digest notes locally:
   ```bash
   ls entities/notes/digest-*.md | sort
   ```

2. Check for existing session summaries:
   ```bash
   ls entities/journals/session-summary-*.md | sort
   ```
   
3. Process digests in chronological order:
   - **Process sequentially, not in parallel** - each summary needs to read previous ones
   - For each digest that doesn't have a corresponding session summary, launch a subagent
   - Wait for each subagent to complete before processing the next date
   - This ensures proper continuity between sessions

```
Generate a session summary for digest-YYYY-MM-DD.md

Instructions:
1. First, run `python scripts/get_entity_overview.py` to get entity names, IDs, and file paths
2. Check if `entities/journals/session-summary-YYYY-MM-DD.md` already exists
3. If it doesn't exist:
   - Find and read 2-3 session summaries from dates BEFORE YYYY-MM-DD for continuity
   - Read the digest from `entities/notes/digest-YYYY-MM-DD.md`
   - The entity overview already provides entity IDs for linking
   - Optionally read select entity files to better understand:
     * Character relationships and personalities
     * Location descriptions and connections
     * Organizational structures
     * BUT REMEMBER: These files contain future events - only use for context, not content
   - Generate a comprehensive session summary following the format below
   - BEFORE SAVING: Review your summary and verify EVERY entity against the overview
   - If any entity with an ID isn't linked, add the link
   - Create the summary as `entities/journals/session-summary-YYYY-MM-DD.md`
4. Report completion or any issues encountered

Summary Generation Instructions:
[Copy all content from "Summary Generation Instructions" section through the end of this document]
```

## Summary Generation Instructions

You are creating comprehensive summaries of Pathfinder 2e tabletop roleplaying sessions based on pre-processed digests. Each digest contains:
- **Session Overview**: Date, previous session recap, key events, party status
- **Chronological Events**: Numbered entries tagged as SCENE, ACTION, DIALOGUE, COMBAT, DISCOVERY, NPC, LOCATION, ITEM, PLANNING, REACTION, SKILL, LORE, CREATURE
- **Combat Summary**: Details of each combat encounter
- **Entities for Extraction**: NPCs, Locations, Quests/Tasks, Organizations with all relevant details
- **Unresolved Questions**: Ambiguities and unclear elements
- **Technical Notes**: Speaker identification issues or unclear segments

### Key Guidelines:
- Use LOCAL entity files in `entities/` for reference and context
- Look up entity details by reading files like `entities/characters/[name].md`
- Create summaries as local journal entries in `entities/journals/`
- Include proper frontmatter with `is_hidden: true`

### Summary Structure

Format each summary using this markdown structure:

```markdown
# [Descriptive Session Title - max 6-7 words]

## Session Overview
A brief (2-3 sentence) overview of the session's main events and accomplishments.

## Story Developments
Write story developments as a flowing narrative, organized chronologically. Use paragraph breaks to separate distinct scenes. Bold important discoveries, names, or items on first mention.

## Combat & Challenges
Describe significant battles narratively, focusing on memorable moments and outcomes rather than mechanics.

## Discoveries & Lore
Outline new world information in clear paragraphs. Include both explicit lore and information gleaned through investigation.

## Quest Updates
* Current primary objective and progress
* New quests acquired
* Quests completed
* Major changes to existing quests

## Next Steps
List known immediate objectives and upcoming challenges. Focus on concrete options rather than speculation.
```

### Processing the Digest:
1. **Review previous session summaries** (if they exist) to understand:
   - Ongoing plot threads and unresolved quests
   - Character relationships and dynamics
   - Recent events that might influence this session
   - The party's current goals and situation
2. **Read the digest thoroughly** to understand the session's flow and key events
3. **Identify major story beats** by looking at:
   - DISCOVERY and LORE entries for plot revelations
   - NPC entries for important character interactions
   - COMBAT entries for significant battles
   - PLANNING entries for party decisions
   - Quest/Task entries in Entities section
4. **Cross-reference with local entities** to add context:
   - Check if NPCs mentioned already exist in `entities/characters/`
   - Look up locations in `entities/locations/` for additional details
   - Review PC files to understand character abilities and relationships
   - **Read entity files to understand**:
     * Character personalities, motivations, and speaking styles
     * Relationships between characters (allies, enemies, family)
     * Location layouts, atmospheres, and connections
     * Organizational hierarchies and goals
     * Combat abilities and typical tactics
   - **IMPORTANT**: Entity files contain the full history including events that happen AFTER this session
   - Use this knowledge to write better narrative (how characters would speak/act)
   - DO NOT include events or facts from entity files that aren't in the digest
   - The digest represents what was known/happened at that specific session date
5. **Synthesize into narrative flow** rather than listing events
6. **Focus on story impact** over mechanical details
7. **Ensure continuity** with previous sessions:
   - Reference callbacks to earlier events when relevant
   - Note progress on ongoing quests
   - Show character development over time
8. **VERIFY ENTITY LINKING**: As you write, constantly check:
   - Is this character in the overview? Link it.
   - Is this location in the overview? Link it.
   - Is this organization/race/deity in the overview? Link it.
   - No entity with an ID should go unlinked

### Formatting Rules:
- Use **bold** for first mentions of significant non-entity items (spells, abilities, important objects without entity records)
- Use *italics* sparingly for emphasis or quotes
- Single-level bullet points only
- Clear paragraphs over nested lists
- Headers (##) only for main sections
- Line breaks between sections

### Name Resolution and Entity Mentions:
- The digest has already resolved most name spellings
- Verify against local entity files when adding context
- Use the exact spellings from the digest's entity extraction section
- For existing entities, you can add details from their local files

### Entity Linking (CRITICAL):
**YOU MUST LINK EVERY ENTITY THAT EXISTS IN THE DATABASE:**
- Check the entity overview for EVERY character, location, organization, etc. you mention
- If it has an ID in the overview, YOU MUST link it on first mention IN EACH PARAGRAPH
- Use the format `[entity:ID|display text]` 
- NO EXCEPTIONS - if an entity has an ID, it gets linked
- Examples of entities you MUST link:
  - Characters: `[entity:7764102|Aelysh]`, `[entity:7763290|Arnór]`
  - Locations: `[entity:7763187|Teghrim's Crossing]`, `[entity:7763870|Menoth-Derith]`
  - Organizations: `[entity:7763122|Dwarven Slayer Cults]`, `[entity:7763864|Goblin Raiders]`
  - Races: `[entity:7763165|Slaan]`, `[entity:7763129|Norn]`
  - Even deities if mentioned: `[entity:7763160|Moradin]`
- Override display text for natural flow:
  - `[entity:7764102|the wood elf]` instead of repeating "Aelysh"
  - `[entity:7763122|the slayer cult]` for variety
- **PARAGRAPH RULE**: Link the first mention in EACH paragraph, not just once per document
- Within a paragraph, only link the first mention
- Before finalizing, VERIFY every entity name against the overview - if it has an ID, it must be linked

### Creating the Journal Entry:
After generating the summary content, create a local journal file:

1. **Filename**: `entities/journals/session-summary-YYYY-MM-DD.md`
   - Example: `entities/journals/session-summary-2025-05-30.md`

2. **File content**:
```markdown
---
name: 2025-05-30 - The Bridge and the Bloodline
type: Session Summary
is_hidden: true
created: '[current timestamp]'
updated: '[current timestamp]'
---

[The full summary content goes here]
```

### Checking for Existing Summaries:
Before creating a new summary:
1. Check if a journal file already exists for this session date
2. Look for files matching pattern: `entities/journals/session-summary-YYYY-MM-DD.md`
3. Only create if no summary exists for that digest date

## Important Notes:
- Each digest represents one complete game session at a specific point in time
- Only mention characters and events that appear in the digest
- Transform the tagged chronological events into flowing narrative
- Preserve important details while making it readable
- The digest has already filtered out out-of-game content
- Use the Entities for Extraction section to ensure all NPCs and locations are mentioned
- **Temporal Warning**: Entity files represent the "current" state with full history - they contain future events relative to the session you're summarizing
- **Only include information that appears in the digest itself** - entity files are just for ID lookups and understanding context

## Writing Style:
- Write in past tense, third person
- Use character names, not player names
- Focus on what happened, not game mechanics
- Make it engaging to read while preserving accuracy
- Bold important names on first mention
- Keep sections distinct but flowing