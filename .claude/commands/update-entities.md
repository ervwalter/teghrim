# Update Entities from Digests

Process session digests to create new entity files and update existing ones with new information.

## Task

1. **Find First Unprocessed Digest**
   - List all files in `entities/notes/` directory that match pattern `digest-YYYY-MM-DD.md`
   - Check if the digest has the "Processed" tag in its frontmatter
   - Identify the FIRST digest without the "Processed" tag in chronological order
   - If all digests are processed, report "All digests have been processed"

2. **Get Entity Context**
   - Run `python scripts/get_entity_overview.py` to see all existing entities
   - This provides a quick reference with correct spellings and file paths
   - **Read all Player Character files** for important context:
     - Read entities/characters/qotal.md
     - Read entities/characters/bruldin-grimstone.md  
     - Read entities/characters/arnór-josefson.md
     - Read entities/characters/aurelia.md
     - Read entities/characters/alrik-grimmelstang.md
     - These files contain crucial background, quests, relationships, and abilities needed for proper entity extraction
   - Use this output to check what already exists before creating new entities

3. **Process the Single Digest**
   - Read the digest file
   - Extract entities from the "Entities for Extraction" section
   - **Also consider Player Characters**: Look for new details about PCs revealed in the session (dialogue, actions, backstory, relationships, abilities demonstrated)
   - **BEFORE creating any new entities**: Ask for spelling clarification on ALL new proper nouns
     - List all new character names, location names, organization names, etc.
     - Ask ONE question at a time: "Should 'Lin Chong' be 'Lyn Chong'?" 
     - Wait for confirmation before proceeding
   - For each entity (including PCs):
     - Check entity overview to see if it already exists
     - **For existing entities**: Read the full entity file to understand current content
     - If new: create the entity file (using confirmed spelling)
     - If exists: update with new information, building on what's already there
   - Add "Processed" tag to the digest's frontmatter tags array

## Entity File Structure

### File Organization
```
entities/
├── characters/       # PCs, NPCs, deities
├── locations/       # Places, regions, landmarks  
├── organizations/   # Groups, factions, guilds
├── races/          # Ancestries, species
├── creatures/      # Monsters, animals
├── quests/         # Missions, tasks, investigations
└── metadata.json   # Defines valid types and tags
```

### Entity File Format (Wikipedia-style)
```markdown
---
name: Entity Name
type: [from metadata.json types list]
tags: [from metadata.json tags list]
is_hidden: false
---

# Entity Name

[One paragraph summary of who/what this is and why they matter - the "evergreen" description that captures their current state and significance]

## Description
### Physical Appearance
[What they look like, distinctive features, typical attire]

### Personality & Demeanor
[How they act, speak, their general disposition - for locations: atmosphere, feel]

### Abilities & Skills
[What they're capable of, known powers, expertise - for locations: defenses, resources]

## Background
[Their origins, how they came to be who they are, formative experiences]

## Relationships
- **[Name]**: [Nature of relationship and current status]
- **[Name]**: [Connection and significance]

## Notable History
[Chronological list of major events, revelations, and developments - written as in-world history, not session notes]

- **The Caravan Ambush**: Demanded toll from travelers, led goblin raiders including spider-mounted units. Killed in combat when challenged.
- **The Bridge Incident**: Revealed connection to larger goblin organization, mentioned missing scouts before the confrontation.

## Current Status
[Where they are now, what they're doing, their immediate situation]

## Secrets & Mysteries
[Unknown elements, unresolved questions, hidden aspects - only if relevant]
```

### metadata.json Structure
The `entities/metadata.json` file defines valid types and tags for each entity category:

- **types**: Primary classification (e.g., "Deity", "NPC", "City")
- **tags**: Additional attributes (e.g., "Greater Deity", "Dramatis Personae")

Special tags for characters:
- **Dramatis Personae**: Major NPCs who are "main characters" of the campaign world (as defined by the campaign's social progression system)

## Processing Guidelines

### Name Resolution
1. **Use the entity overview output** from step 2 for quick reference
2. **For potential matches**: Read the full entity file to understand context
3. Common variations to check:
   - Spelling differences (e.g., "Lin" vs "Lyn")
   - Partial names (e.g., "Grimstone" vs "Bruldin Grimstone")
   - Titles (e.g., "Captain Smith" vs "Smith")
4. **Use Grep tool** to search entity contents if unsure:
   - `grep -i "search_term" entities/characters/*.md`
   - Helps find entities mentioned in other files
5. When uncertain, mark as [AMBIGUITY] for user confirmation

### New Entity Creation
1. **Confirm spelling first** - ask for clarification on any uncertain proper nouns
2. Use kebab-case for filenames: `entity-name.md`
3. Set initial type based on digest information
4. Add appropriate tags (check metadata.json)
5. Write a comprehensive Overview paragraph
6. Populate all relevant sections with information from the digest
7. Write history events as in-world occurrences, not game sessions

### Existing Entity Updates
1. **Read the full entity file first** to understand what's already documented
2. **Preserve existing content** - never delete information
3. **Enhance the Overview** if new information changes their significance
4. **Update evergreen sections**:
   - Merge new physical details into Description
   - Update Current Status to reflect latest events
   - Add new Relationships as they're revealed
5. **Add to Notable History**:
   - Check existing history to maintain continuity
   - Write new events as historical occurrences
   - Use descriptive event names (e.g., "The Goblin Toll Incident")
   - Keep chronological order
   - No session dates or meta-references
6. **Cross-reference with related entities**:
   - **Read related entity files** for context before making updates
   - If updating a character, read locations they're associated with
   - If updating an organization, read its members' files
   - If updating a location, read characters and organizations connected to it
   - If entities mention each other, read both files to ensure consistent information
   - Use the Grep tool to find connections: `grep -i "entity_name" entities/*/*.md`
   - Ensure consistency across related entities
7. **Refine existing sections**:
   - If new info contradicts old, note the change in history
   - Update personality based on observed behavior
   - Expand abilities as they're demonstrated
8. **Player Characters receive the same treatment**:
   - Update PC files with new dialogue, actions, and character development
   - Add relationships formed with NPCs and other PCs
   - Document abilities used, backstory revealed, or personality traits shown
   - Treat PCs as entities that grow and develop through play

### Wikipedia-style Writing Guidelines
- **Write in-world**: As if documenting real people/places in the campaign world
- **Present tense for current state**: "Lyn Chong is an elderly monk..."
- **Past tense for history**: "During the caravan journey, he revealed..."
- **No meta-references**: Don't mention sessions, players, dice rolls, or game mechanics
- **Named events**: Give significant occurrences memorable names
- **Comprehensive**: Each entity should stand alone as a complete reference

### Handling Changes Over Time
When information changes or evolves:
1. **Update the Overview** to reflect the current state
2. **Note the change in Notable History**: "Following the Bridge Incident, the goblin tribes reorganized under new leadership"
3. **Keep the Description current**: If someone loses an eye, update their physical description
4. **Archive old status**: Move previous "Current Status" info to history if significantly different
5. **Contradictions**: Note them in history: "Previously thought to be from the Iron Kingdoms, later revealed their true origin as..."

### Location Entity Example
```markdown
# Teghrim's Crossing

Teghrim's Crossing is a bustling bridge-city built upon an ancient dwarven bridge spanning a massive river canyon. The settlement serves as a crucial trade hub connecting eastern and western lands, with the entire town constructed along and around the bridge structure itself.

## Description
### Physical Layout
The city stretches across a colossal stone bridge of dwarven construction, with buildings rising from the bridge deck in a mixture of architectural styles. Original dwarven stonework forms the foundation, while human wooden structures and mixed construction have been added over centuries.

### Atmosphere
A constant flow of merchants, travelers, and locals creates a vibrant market atmosphere. Guards stationed at both ends check incoming traffic, while the mix of races and cultures makes it one of the most cosmopolitan settlements in the region.

### Notable Features
- Ancient dwarven bridge architecture with later additions
- Buildings constructed directly on the bridge
- Defensive positions at both ends
- Market squares built into wider sections

## Notable History
- **The Original Construction**: Built by ancient dwarven engineers for unknown purposes, the bridge predates all current civilizations
- **The Settlement Founding**: Traders began using the bridge as a meeting point, eventually establishing permanent structures
- **The Eastern Expansion**: Recent trade agreements with Jade Kingdoms increased traffic and prosperity

## Current Status
Thriving trade hub with increasing importance as eastern trade routes develop. Recent goblin activity on approach roads has raised security concerns.
```

### Organization Entity Structure
Organizations should follow similar patterns:
- **Overview**: Current purpose and influence
- **Description**: Structure, leadership, symbols, methods
- **Background**: Founding, evolution, major turning points
- **Notable Members**: Key figures and their roles
- **Activities**: Current operations and goals
- **Relationships**: Allies, enemies, neutral parties

### Quest/Task Entities
Quests deserve their own entity files when they:
- Span multiple sessions
- Involve significant effort or risk
- Have clear objectives and stakes
- Include major battles or investigations

Quest structure follows the same Wikipedia-style format, treating the quest as a historical event or ongoing situation rather than a game mechanic.

## Ambiguity Handling

When encountering ambiguities:
1. **For new entities**: Mark unclear spellings and ask for clarification
   - "The digest mentions 'Tegrim's Crossing' - should this be 'Teghrim's Crossing'?"
   - "Found NPC 'Lin Chong' - is this the same as existing 'Lyn Chong'?"
   - "Location 'Memphold Daroth' appears - confirm spelling or connection to 'Menoth-Derith'?"
2. **After receiving spelling corrections**: Update the digest file to fix all instances of the misspelling
   - Use the Edit tool to replace incorrect spellings throughout the digest
   - Ensure consistency between the digest and the entities you create
3. Create entities with [AMBIGUITY] markers for uncertain elements
4. After processing all entities, list ambiguities for user **one at a time**
5. Common ambiguities:
   - Is this the same person as existing entity X?
   - What type should this organization be?
   - Is this a Dramatis Personae?
   - Spelling variations for names, locations, organizations
6. **Always confirm spelling** for new proper nouns before creating files

## Best Practices for Entity Research

When processing entities:
1. **Use the entity overview** as your primary index
2. **Read full files** for entities you're updating - don't rely on overview alone
3. **Read related entities** before making updates:
   - If updating Lyn Chong, also read files for Qotal (spiritual connection) and locations mentioned
   - If updating Teghrim's Crossing, read files for characters who have been there
   - If updating a quest, read files for all participants and relevant locations
4. **Search for connections** using Grep:
   - Find all mentions of a character: `grep -i "character_name" entities/*/*.md`
   - Find related organizations: `grep -i "organization_name" entities/*/*.md`
   - Search for location names to find all connected entities
5. **Check multiple spellings** when searching
6. **Build on existing content** rather than duplicating
7. **Maintain narrative consistency** across all connected entities

## Output

After processing:
1. Report number of new entities created
2. Report number of existing entities updated  
3. List any ambiguities that need resolution
4. Update the digest to add "Processed" tag
5. Provide summary of major additions
6. Note any cross-references or connections discovered

Begin by finding the first unprocessed digest and generating the entity overview.