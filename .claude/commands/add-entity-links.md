# Add Entity Links

This command systematically reviews all entity files (except notes and journals) and adds entity links where they're missing, using the entity overview to find IDs. Journals are excluded because they get proper links when generated.

## Usage

Run this command to scan all entity files and add `[entity:ID|text]` links wherever entities are mentioned but not yet linked.

## Process

1. Find all entity markdown files (excluding notes and journals):
   ```bash
   find entities/ -name "*.md" -type f | grep -E "(characters|locations|organizations|races|creatures|quests)" | grep -v -E "entities/(notes|journals)/" | sort
   ```

2. Group entities into batches (e.g., 10-15 files per batch)

3. Process each batch sequentially (one at a time), launching a subagent for each batch:

```
Add entity links to the following files: [list of files]

Instructions:
1. First, run `python scripts/get_entity_overview.py` to get all entity names and their IDs
2. Read all files in your batch IN PARALLEL to understand their content
3. For each file in your batch:
   - Scan for any mention of entities that exist in the overview
   - Check if they're already linked (look for [entity:ID|text] format)
   - If not linked on first mention IN THAT PARAGRAPH, add the link
   - Use natural display text that fits the context
   - Link the FIRST mention in EACH PARAGRAPH (not just once per document)
4. Guidelines:
   - Don't link an entity to itself (e.g., don't link "Moradin" in Moradin's own file)
   - Preserve existing links - don't change them
   - Use varied display text: [entity:7764102|Aelysh], [entity:7764102|the wood elf], etc.
   - For possessives: [entity:7764102|Aelysh's]
   - For partial mentions, use full link: "the Crossing" → [entity:7763187|the Crossing]
5. Save the updated file only if changes were made
6. Report: "Updated X files: [list]" or "No updates needed for batch"

Entity matching rules:
- Full names: "Teghrim's Crossing" → link it
- Partial but clear: "the Crossing" (when clearly referring to Teghrim's) → link it  
- Common variations: "Dwarven Slayer Cult" or "slayer cult" → link to "Dwarven Slayer Cults"
- Character nicknames if established in context
- Organization abbreviations if clear from context
```

4. After each subagent completes, collect its report before moving to the next batch

5. After all batches are processed, summarize the total changes made across all files

## Important Guidelines

### What to Link:
- Character names (PCs, NPCs, deities)
- Location names (cities, regions, buildings)
- Organization names (guilds, cults, governments)
- Race/ancestry names when referring to the general type
- Creature types when referring to the general category
- Any other entity with an ID in the overview

### What NOT to Link:
- The entity's own name within its own file
- Generic terms that happen to match ("crossing" as a verb)
- Entities already linked in that paragraph (second+ mentions)
- Text within quotes if it would break the flow
- Names in frontmatter or metadata sections
- Note files are excluded entirely (digests, rules references, etc.)
- Journal files are excluded (session summaries have links added during generation)

### Special Cases:
- **Partial mentions**: "the Crossing" → `[entity:7763187|the Crossing]` if clearly Teghrim's
- **Possessives**: "Moradin's temple" → `[entity:7763160|Moradin's]` temple  
- **Plural/variations**: "slayer cults" → `[entity:7763122|slayer cults]`
- **In lists**: Each item in a list can have its own first mention
- **New paragraphs**: Each paragraph gets fresh linking - link first mention even if linked in previous paragraph

### Quality Checks:
- Ensure display text reads naturally in context
- Don't over-link - one link per entity per paragraph is the rule
- Preserve the original meaning and flow
- Check that links work with surrounding punctuation

## Example Transformations

Before:
```
Bruldin is a member of the Dwarven Slayer Cults, having taken the oath after his family was killed. He arrived at Teghrim's Crossing seeking glorious death.
```

After:
```
Bruldin is a member of the [entity:7763122|Dwarven Slayer Cults], having taken the oath after his family was killed. He arrived at [entity:7763187|Teghrim's Crossing] seeking glorious death.
```

Before:
```
The party met Aelysh at her treehouse. The wood elf offered them aid.
```

After:
```
The party met [entity:7764102|Aelysh] at her treehouse. The wood elf offered them aid.
```

## Benefits

- Improves navigation in Kanka by linking related entities
- Ensures consistency across all entity files  
- Makes relationships between entities clearer
- Enhances the user experience when browsing the campaign

## Notes

- This is a one-time cleanup operation, though it can be run periodically
- New entities should have links added when created
- The script is idempotent - running it multiple times won't create duplicate links
- Focus on clarity and readability over maximum linking