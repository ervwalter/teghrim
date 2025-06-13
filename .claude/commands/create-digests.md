# Create Session Digests

Process raw RPG session transcripts into structured digests that preserve all meaningful game content while dramatically reducing size.

## Task

1. **Find First Unprocessed Transcript**
   - Check `transcripts/` for all session transcripts (YYYY-MM-DD.md files)
   - Check if corresponding digest exists in `entities/notes/digest-YYYY-MM-DD.md`
   - Identify the FIRST unprocessed transcript in chronological order
   - Report which transcript will be processed
   - If all transcripts have digests, report "All transcripts have been processed"

2. **Process the Single Transcript Using Subagents**
   - **IMPORTANT**: Process ONLY the first unprocessed transcript
   - First, run `python scripts/get_entity_overview.py > .digests_temp/entity_overview.md` to create reference
   - **Read all Player Character files** for context:
     - Read entities/characters/qotal.md
     - Read entities/characters/bruldin-grimstone.md  
     - Read entities/characters/arnór-josefson.md
     - Read entities/characters/aurelia.md
     - Read entities/characters/alrik-grimmelstang.md
     - These provide crucial context for character names, abilities, quests, and relationships
   - Create temp directory: `mkdir -p .digests_temp`
   - If a previous digest exists, copy its key information to `.digests_temp/previous_digest_summary.md`
   - **Subagent Strategy** (to manage context limits):
     - Check the transcript line count using `wc -l`
     - For typical 4-hour transcripts (~8000 lines), create 8-10 subagent tasks
     - Each subagent processes ~1000 lines with 200-line overlap:
       - Task 1: "Process lines 1-1000 of transcripts/YYYY-MM-DD.md following the digest format below. Check .digests_temp/entity_overview.md for name resolution. Return a partial digest with events from this section."
       - Task 2: "Process lines 800-1800 of transcripts/YYYY-MM-DD.md..." (overlap for context)
       - Task 3: "Process lines 1600-2600 of transcripts/YYYY-MM-DD.md..."
       - Continue with appropriate line ranges
     - Give each subagent:
       - The digest format template
       - Access to entity overview
       - Instructions to mark ambiguities
       - Previous chunk summary if relevant
   - **Save each partial digest to temp files**:
     - Task 1 result → `.digests_temp/digest_chunk_1.md`
     - Task 2 result → `.digests_temp/digest_chunk_2.md`
     - Continue for all chunks
   - **Combine and refine**:
     - Read each chunk file sequentially (not all at once)
     - Create `.digests_temp/digest_combined.md` with merged events
     - Use `grep` or `sed` to find and remove duplicate events from overlap
     - Build unified entity extraction section in `.digests_temp/entities_to_extract.md`
     - Combine all sections into final digest
   - Save to `digests/YYYY-MM-DD.md`
   - Clean up temp files: `rm -rf .digests_temp/`
   
3. **Handle Ambiguities (IMPORTANT)**
   - **BE PROACTIVE** about asking for clarification on uncertain elements
   - If you encounter ANY ambiguities (character identity, spelling variations, unclear events, uncertain speaker mappings):
     - Save a draft of the digest with clear [AMBIGUITY] markers
     - **Ask ONE question at a time** - prioritize the most important ambiguity first
     - Examples: "Is 'Lyn' and 'Lynn' the same character?", "Does 'the dwarf' refer to Bruldin or Alrik?", "Speaker 16 seems to be talking about divine quests - is this Qotal?"
     - After receiving an answer, update the draft and ask about the next ambiguity if needed
   - **Common ambiguities to watch for**:
     - Character name variations or unclear speaker assignments
     - Whether events are in-character or out-of-character
     - Spell names, location names, or proper nouns that are unclear
     - Timeline or sequence confusion
   - Continue this process until all significant ambiguities are resolved
   - **Do not finalize the digest** until all ambiguities are resolved
   
4. **Finalize**
   - After resolving any ambiguities, save the final digest to `entities/notes/digest-YYYY-MM-DD.md`
   - Add frontmatter:
     ```yaml
     ---
     name: Session Digest - YYYY-MM-DD
     type: Session Digest
     tags: [Digest]
     is_hidden: true
     created: 'YYYY-MM-DDTHH:MM:SS+00:00'
     updated: 'YYYY-MM-DDTHH:MM:SS+00:00'
     ---
     ```
   - **IMPORTANT**: Use exact filename format `digest-YYYY-MM-DD.md`
   - Remove any temporary files created during processing
   - Report: "Digest for YYYY-MM-DD complete and saved to entities/notes/"
   - Do NOT process additional transcripts - the user will run the command again if needed

## Processing Instructions

### Context Understanding
- These are tabletop RPG (D&D/Pathfinder) session transcripts
- Speaker numbers (Speaker 1, Speaker 2, etc.) are NOT consistent across the transcript due to concatenation of ~2 hour segments
- Players speak both IN CHARACTER (as their fictional characters) and OUT OF CHARACTER (discussing rules, making jokes, scheduling, etc.)
- Transcription often has spelling errors and inconsistencies for character names, places, and game terms

### Name Resolution
Use the `entities/` directory to help resolve spelling inconsistencies:
- **RECOMMENDED**: First run `python scripts/get_entity_overview.py` to get a quick reference of all entities
  - This shows player-to-character mappings clearly (e.g., "Erv plays Qotal")
  - Provides entity names, types, and brief descriptions
  - Helps identify correct spellings quickly
- If you need more detail, check specific directories:
  - `entities/characters/` for PC, NPC, and deity names
  - `entities/locations/` for place names
  - `entities/races/` for ancestry/species names
  - `entities/organizations/` for faction names
- When you find a likely match (e.g., "Moridan" → "Moradin"), use the correct spelling from the entity files

### Content Filtering
**INCLUDE:**
- All in-game narrative events (even minor ones)
- Character actions and decisions (including failed attempts)
- ALL dice rolls with context and outcomes
- Combat sequences (break down significant rounds/attacks)
- Important dialogue and roleplay
- Character interactions and reactions
- Environmental descriptions and atmosphere
- Party planning and strategy discussions
- Skill checks and their purposes
- Clues, plot points, and story developments
- New NPCs, locations, or items introduced
- Character development moments
- Lore drops and world-building details
- Emotional beats and character reactions

**EXCLUDE:**
- Out-of-character discussions about:
  - Food orders and eating
  - Bathroom breaks
  - Technical issues (mics, software, etc.)
  - Scheduling future sessions
  - Real-world topics unrelated to game
  - Rules clarifications (unless they affect story)
- Meta-gaming discussions
- Repeated failed attempts at the same action

### Digest Format

```markdown
# Session Digest: YYYY-MM-DD

## Session Overview
- **Date**: [Session date]
- **Previous Session**: [Brief 1-2 sentence recap if previous digest exists]
- **Key Events**: [2-3 bullet points summarizing major developments]
- **Party Status**: [Current location, condition, immediate goals]

## Chronological Events

### [Time Range: HH:MM - HH:MM]
1. **SCENE**: [Environmental description or GM narration]
2. **ACTION**: [Character name, not Speaker #] attempts [action] → [roll result if applicable] → [outcome]
3. **DIALOGUE**: [Character name, not Speaker #] to [Character]: "[Key dialogue - preserve specific details, names, places mentioned]"
4. **COMBAT**: [Detailed combat summary - include creature types, mount descriptions, special abilities used, significant individual attacks/spells]
5. **DISCOVERY**: [Clue, revelation, or important information gained]
6. **NPC**: [Name] ([role]) - [brief description if first appearance]
7. **LOCATION**: Arrived at/Departed [Location] - [brief description if new]
8. **ITEM**: [Character] obtained/used [Item] - [brief description]
9. **PLANNING**: [Party discusses strategy or makes decisions]
10. **REACTION**: [Character]'s response to [event] - [emotional/physical reaction]
11. **SKILL**: [Character] uses [skill/ability] for [purpose] → [outcome]
12. **LORE**: [World-building information or backstory revealed - include specific names, dates, historical events]
13. **CREATURE**: [Creature type] - [Physical description, behavior, special abilities observed]

[Continue chronologically through session...]

## Combat Summary
- **[Combat 1]**: [Location] - [Participants] vs [Enemy types with descriptions, including mounts/special units] → [Outcome and key tactical elements]
- [Continue for each combat]

## Entities for Extraction

### NPCs
- **[Name]**: [All relevant information from this session - appearance, personality, role, actions, dialogue, relationships, items carried, location encountered]

### Locations  
- **[Name]**: [All relevant information - description, layout, inhabitants, events that occurred there, connections to other locations, notable features]

### Quests/Tasks
- **[Title]**: [Description, who assigned it, objectives, current progress, participants, stakes, complications, rewards if completed]
Note: Include major battles, investigations, rescue missions, or any task requiring significant effort

### Organizations
- **[Name]**: [Type, members encountered, stated goals, activities observed, relationships to other groups, locations associated with]

## Unresolved Questions
- [Ambiguities in transcript or story]
- [Unclear character identities or spelling]
- [Potential plot threads]

## Technical Notes
- [Any significant speaker identification issues]
- [Transcript segments that were particularly unclear]
```

### Processing Guidelines
1. Preserve ALL plot-relevant information with SPECIFIC DETAILS
2. Use consistent character names throughout (resolved from entities/ and previous digests)
3. Group events into logical time blocks (usually 10-15 minute chunks for more detail)
4. Maintain chronological order strictly
5. When uncertain if content is in-game or out-of-game, include it with a note
6. For combats:
   - List ALL creature types involved (e.g., "goblins riding giant spiders")
   - Note special units or abilities (e.g., "squigs", "spider mounts")
   - Include tactical elements and positioning
7. For dialogue and lore:
   - Preserve specific details (names, places, historical events)
   - Don't just say "discussed background" - include WHAT was revealed
   - Character motivations should be specific, not general
8. **Event Density**: Aim for comprehensive coverage - include minor actions, reactions, and atmospheric details
   - A 4-hour session should typically produce 80-120+ events
   - Break down complex scenes into multiple events
   - Capture the flow of conversation, not just outcomes
9. **Continuity**: Reference previous digest to ensure:
   - Character names match established spellings
   - Ongoing plot threads are recognized
   - Party dynamics and relationships are understood
   - Location transitions make sense
10. **Ambiguity Handling (CRITICAL)**:
   - **ALWAYS mark unclear sections** with [AMBIGUITY: description]
   - **DO NOT GUESS** - ask for clarification instead
   - Common ambiguities: character identity, spell names, location names, whether something was IC or OOC
   - **STOP and ASK** rather than making assumptions about unclear content
   - Better to have a partial digest with clear questions than a complete digest with wrong information

### Common Pitfalls to Avoid
1. **Missing creature details** - Always describe what enemies look like and what they're riding/using
2. **Vague character motivations** - Be specific (not "divine mission" but "following a carved line on a statue")
3. **Generic scene descriptions** - Include specific details shared in campfire/social scenes
4. **Overlooking unique elements** - Note special creatures, weapons, or abilities (like squigs, spider mounts)
5. **Assuming proper names** - "Caravan serai" is a type of building, not a specific place name

### Chunk Processing Details
When processing chunks, maintain consistency:
1. **Track speaker mappings** across chunks (Speaker 1 in chunk 1 might be Speaker 3 in chunk 2)
2. **Preserve ongoing scenes** - if a scene spans chunks, note it continues
3. **Time continuity** - ensure chronological flow between chunks
4. **Format each chunk digest** with:
   ```
   ## Chunk N: Lines XXXX-YYYY (HH:MM:SS - HH:MM:SS)
   ### Events
   [Chronological event list]
   ### Ambiguities in this chunk
   [List any unclear elements]
   ```

### Subagent Task Template
When creating subagent tasks for chunk processing, use this template:

```
Process lines [START]-[END] of transcripts/YYYY-MM-DD.md into a partial digest.

Resources available:
- .digests_temp/entity_overview.md - Quick reference of all entities with correct spellings
- .digests_temp/previous_chunk_summary.md - Summary of what happened in the previous chunk (if applicable)

Instructions:
1. Read the specified lines using: Read tool with offset=[START] limit=[END-START]
2. Create a digest following this exact format:
   [Include the event format template from above]
3. Save your digest to: .digests_temp/digest_chunk_[N].md
4. Also create: .digests_temp/chunk_[N]_summary.md with a 2-3 sentence summary for the next chunk

Important guidelines:
1. Include ALL in-game events, even minor ones
2. **CRITICAL: Convert all speaker numbers to character names**
   - Check .digests_temp/entity_overview.md for player mappings
   - Speaker numbers change between segments - use context clues
   - If unsure, mark as [AMBIGUITY: Speaker X might be Character Y]
   - NEVER leave "Speaker 16" in the final output - always resolve or mark ambiguous
3. Mark ambiguities with [AMBIGUITY: description]
4. Include creature descriptions in combat (e.g., "goblins riding giant spiders")
5. Preserve specific details in dialogue and lore
6. Note timestamp ranges covered

Common name resolutions:
- Real player names (Erv, Kent, Katie, Michael, Matt) → Their character names
- GM/DM/Craig → Always use "GM" 
- Check previous chunk summary for ongoing character identifications

Do not return the digest content in your response - just confirm it was saved to the file.
```

### Managing Context Limits
Since transcripts can use 90%+ of context:
1. Use subagents for the heavy lifting of reading and initial processing
2. Keep your own context clear for coordination and final assembly
3. Save intermediate results to temp files if needed
4. Focus on merging and refining rather than initial processing

### Entity Extraction Guidelines
When populating the "Entities for Extraction" section:
1. **Capture all relevant details** from this session, even if the entity might already exist
2. **Don't check if entities are new** - just record what you learn about them
3. **Items go within entity descriptions** - e.g., note that an NPC carries a specific weapon
4. **Quests include any significant effort** - battles, investigations, not just literal quests
5. **Use consistent naming** based on your name resolution from earlier in the process

## Output

After creating the digest:
1. Report the digest filename created
2. Note any significant name resolutions made
3. List any ambiguities that couldn't be resolved
4. Provide a brief summary of the session's main plot developments
5. Note the number of entities captured for extraction
6. State if there are more unprocessed transcripts remaining

Begin by finding the first unprocessed transcript and processing only that one.