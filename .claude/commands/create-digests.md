# Create Session Digests

Process raw RPG session transcripts into structured digests that preserve all meaningful game content while dramatically reducing size.

**IMPORTANT**: Use thinking mode throughout this task to carefully analyze transcript content, validate subagent work, and ensure accuracy.

## Task Overview

1. **Find First Unprocessed Transcript**
   - Check `transcripts/` for all session transcripts (YYYY-MM-DD.md files)
   - Check if corresponding digest exists in `entities/notes/digest-YYYY-MM-DD.md`
   - Identify the FIRST unprocessed transcript in chronological order
   - Report which transcript will be processed
   - If all transcripts have digests, report "All transcripts have been processed"

2. **Study Existing Digest Format FIRST**
   - **CRITICAL**: Before processing anything, read these example digests to understand the ACTUAL format:
     - `entities/notes/digest-2025-09-26.md` (read lines 1-200)
     - `entities/notes/digest-2025-09-12.md` (read lines 1-150)
   - The format uses:
     - Numbered chronological events with timestamps: `1. **TAG**: [HH:MM:SS] Description`
     - Tags: **SCENE**, **ACTION**, **DIALOGUE**, **COMBAT**, **DISCOVERY**, **LORE**, **NPC**, **LOCATION**, **ITEM**, **PLANNING**, **REACTION**, **SKILL**, **CREATURE**, **MECHANICS**, **OOC**
     - Exact quotes with context
     - Granular detail (150-250+ events for 4-hour sessions)
   - **DO NOT use a simplified format** - match the existing digests exactly

3. **Prepare for Processing**
   - Create temp directory: `mkdir -p .digests_temp`
   - Run `python scripts/get_entity_overview.py > .digests_temp/entity_overview.md`
   - Read all Player Character files for context:
     - entities/characters/qotal.md
     - entities/characters/bruldin-grimstone.md
     - entities/characters/arnor-josefson.md
     - entities/characters/aurelia.md
     - entities/characters/alrik-grimmelstang.md
   - Use semantic search to understand recent storylines (search session dates, character names, ongoing quests)
   - If previous digest exists, create `.digests_temp/previous_digest_summary.md` with key context

4. **Process Using Subagents**
   - Check transcript length: `wc -l transcripts/YYYY-MM-DD.md`
   - For typical 4-hour sessions (~8000 lines): create 10 subagent tasks
   - Each processes ~1000 lines with 200-line overlap for context:
     - Chunk 1: lines 1-1000
     - Chunk 2: lines 800-1800
     - Chunk 3: lines 1600-2600
     - Continue pattern through entire transcript
   - Save chunks to: `.digests_temp/digest_chunk_N.md`
   - Each chunk includes summary for next: `.digests_temp/chunk_N_summary.md`

5. **Combine and Validate**
   - Read chunks sequentially (don't load all at once)
   - Remove duplicate events from overlap regions
   - Validate timeline, character consistency, event flow
   - If something seems wrong, re-read original transcript sections
   - Create unified digest matching existing format exactly

6. **Handle Ambiguities (MANDATORY)**
   - **STOP AND ASK** before finalizing
   - Mark all unclear items with [AMBIGUITY: description]
   - Present grouped list to user for clarification
   - Common issues: character names, spell attribution, IC/OOC distinction, location spellings
   - **Do not finalize until user confirms corrections**

7. **Finalize**
   - Save to `entities/notes/digest-YYYY-MM-DD.md` with frontmatter:
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
   - Clean up: `rm -rf .digests_temp/`
   - Report completion with summary

## Processing Instructions

$arguments

### Core Principles
1. **Accuracy Over Completeness**: Better to have less content that's correct
2. **Skepticism Over Assumption**: Question everything unusual
3. **Clarity Over Brevity**: Include context even if longer
4. **Verification Over Speed**: Take time to check entities
5. **Questions Over Guesses**: Always ask when uncertain
6. **Format Matching**: Follow existing digests exactly, not simplified templates

### Player-to-Character Mappings
**CRITICAL - Correct mappings**:
- Erv (player) → Qotal (character)
- Kent (player) → Alrik (character)
- Michael (player) → Bruldin (character)
- Katie (player) → Aurelia (character)
- Matt (player) → Arnor (character)

### Context Understanding
- Pathfinder 2e Remastered campaign
- Speaker numbers NOT consistent across transcript (concatenated ~2 hour segments)
- Players speak IN CHARACTER (as fictional characters) and OUT OF CHARACTER (rules, jokes, scheduling)
- Transcription has spelling errors and inconsistencies
- Use PF2e knowledge for items, spells, combat mechanics, conditions
- Common terms: "flurry" (monk), "hero points", "dying condition", "flat-footed"

### Session Type Recognition
1. **Normal Session**: Full audio recording with continuous gameplay
2. **Recap Session**: Players discussing/remembering lost session (like 06-13) - include MORE detail, preserve all attempts to remember, tag with **RECAP**
3. **Partial Session**: Technical issues or incomplete recording

### Name Resolution Strategy
1. Run `python scripts/get_entity_overview.py` for quick reference (shows "Erv plays Qotal" mappings)
2. Use semantic search with `extensionFilter: [".md"]` for phonetic matches:
   - "Moridan deity dwarf" → Moradin
   - "Not-Vig character NPC" → Natvig
   - "Kingram's Crossing bridge" → Teghrim's Crossing
3. Verify unusual names before accepting (don't assume jokes/wordplay)
4. Cross-reference entity files for correct spellings

### Participant Verification
1. Identify who is physically present at session start
2. Check for explicit statements: "X wasn't here" or "only Y, Z present"
3. Cross-reference against character actions in transcript
4. Mark [AMBIGUITY: Participant list unclear] if unsure
5. Note if players join/leave mid-session

### Content Filtering

**INCLUDE:**
- All in-game narrative events (even minor)
- Character actions/decisions (including failures)
- ALL dice rolls with context/outcomes
- Combat sequences (individual rounds/attacks)
- Dialogue and roleplay (exact quotes)
- Character interactions/reactions
- Environmental descriptions
- Planning and strategy
- Skill checks with purposes
- Plot developments and clues
- New NPCs/locations/items
- Lore and world-building
- Emotional beats

**EXCLUDE:**
- OOC discussions: food, breaks, technical issues, scheduling, unrelated real-world topics
- Meta-gaming discussions
- Repeated failed attempts at same action

### Digest Structure Requirements

**Frontmatter** (YAML):
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

**Header Section**:
```markdown
# Session Digest - YYYY-MM-DD

**Session Date**: [Real date]
**In-game Dates**: [Game dates covered]
**Location**: [Primary location]
**Timestamp Range**: [HH:MM:SS] - [HH:MM:SS]

## Session Overview
[Paragraph summary of major events]

## Participants
**Player Characters**:
- Character Name (Player Name) - [participation notes]

**NPCs Encountered/Accompanying**:
- [List with roles]

**Previous Session Context**: [1-2 sentence recap]
```

**Combat Summary** (if applicable):
```markdown
## Combat Summary

### Combat 1: [Title] ([In-game date/time])
**Location**: [Where]
**Duration**: [Timestamp range]
**Enemies**: [Types with descriptions]
**Outcome**: [Result]

**Combat Mechanics Discovered**:
- [Bullet points of special abilities, resistances, etc.]

**Key Moments**:
- [Narrative highlights with quotes]
```

**Chronological Events** (MAIN SECTION):
```markdown
## Chronological Events

### [Section Header with time/date range]

1. **TAG**: [HH:MM:SS] Description with exact quotes, rolls, outcomes
2. **TAG**: [HH:MM:SS] Next event...
[Continue numbered throughout entire session]
```

**Entities for Extraction**:
```markdown
## Entities for Extraction

### NPCs
- **Name**: All session info - appearance, personality, role, actions, dialogue, relationships, items, location

### Locations
- **Name**: Description, layout, inhabitants, events, connections, features

### Creatures
- **Name/Type**: Physical description, abilities, behavior

### Quests/Tasks
- **Title**: Description, assigner, objectives, progress, participants, stakes, complications

### Organizations
- **Name**: Type, members, goals, activities, relationships, locations

### Items
- **Name**: Description, properties, who has it, how obtained
```

**Closing Sections**:
```markdown
## Unresolved Questions
- [Ambiguities, unclear elements, plot threads]

## Technical Notes
- [Speaker ID issues, unclear segments, corrections made]

## Continuity Notes
**From Previous Session**: [Key connections]
**Into Next Session**: [Setup for continuation]
```

### Event Density Requirements

**A 4-hour session MUST have 150-250+ numbered events**

Event breakdown guidelines:
- **Social encounters**: 10-15 events showing back-and-forth dialogue
- **Combat rounds**: Individual attacks/spells/abilities, not summaries
- **NPC conversations**: Multiple **DIALOGUE** entries, not single **LORE** summaries
- **Downtime**: Each character's activities detailed separately
- **Failed attempts and comedy**: Always include
- **Minor actions**: Environmental interactions, reactions, planning discussions

**If your digest has <100 events for a 4-hour session, you've compressed too much.**

### Accuracy Standards
1. **NO HALLUCINATION**: Only include what's clearly in transcript
2. **NO ASSUMPTIONS**: Mark ambiguities with [AMBIGUITY: description]
3. **VERIFY EVERYTHING**: Cross-check against entity files
4. **EXACT QUOTES**: Don't paraphrase dialogue
5. **SKEPTICAL APPROACH**: Question unusual elements, verify spelling, check game mechanics

### Quality Checklist
Before finalizing, verify:
- [ ] Matches format of entities/notes/digest-2025-09-26.md
- [ ] All character names match entity files (no "Speaker X" remains)
- [ ] All participants confirmed present
- [ ] Items/spells match PF2e or entity files
- [ ] IC/OOC properly distinguished
- [ ] No assumed information added
- [ ] All ambiguities resolved or marked
- [ ] Dates and timeline consistent
- [ ] 150-250+ events for 4-hour session
- [ ] Major NPCs have 3-5+ dialogue quotes each
- [ ] Combat includes tactical details
- [ ] Player humor/meta-commentary preserved
- [ ] Failed attempts and comedy included

### Subagent Task Template

```
Process lines [START]-[END] of transcripts/YYYY-MM-DD.md into a partial digest.

**CRITICAL**: Before starting, read entities/notes/digest-2025-09-26.md (lines 1-200) to see the EXACT format expected.

Resources available:
- .digests_temp/entity_overview.md - Entity reference with player mappings
- .digests_temp/chunk_[N-1]_summary.md - Previous chunk summary (if applicable)

Instructions:
1. Read specified lines: Read tool with offset=[START] limit=[END-START]
2. Create digest matching format from entities/notes/digest-2025-09-26.md:
   - Numbered events with timestamps: `1. **TAG**: [HH:MM:SS] Description`
   - Use tags: SCENE, ACTION, DIALOGUE, COMBAT, DISCOVERY, LORE, NPC, LOCATION, ITEM, PLANNING, REACTION, SKILL, CREATURE, MECHANICS, OOC
   - Exact quotes for all dialogue
   - Specific details for everything
3. Save to: .digests_temp/digest_chunk_[N].md
4. Create: .digests_temp/chunk_[N]_summary.md (2-3 sentence summary for next chunk)

Critical guidelines:
1. **20+ events per 1000 lines minimum**
2. **Convert ALL speaker numbers to character names**:
   - Erv→Qotal, Kent→Alrik, Michael→Bruldin, Katie→Aurelia, Matt→Arnor
   - Check .digests_temp/entity_overview.md for verification
   - Speaker numbers change between segments - use context clues
   - Mark [AMBIGUITY: Speaker X might be Character Y] if unsure
   - NEVER leave "Speaker 16" in output
3. **Preserve exact dialogue** with context tags: "(laughs)", "(sarcastically)"
4. **Include creature descriptions** in combat
5. **Expand social encounters** - show back-and-forth, not just outcomes
6. **Note NPC personality** - speech patterns, quirks, reactions
7. **Mark all ambiguities** with [AMBIGUITY: description]
8. **Distinguish IC/OOC**:
   - Third-person ("Qotal's really good...") = likely OOC
   - First-person in-character ("I attack") = IC
   - Real-world topics = OOC
   - Default to OOC for meta-discussions

Game context:
- Pathfinder 2e Remastered campaign
- Verify names against entity overview
- Question transcription oddities
- NEVER add information not in transcript

Confirm file save only - don't return content.
```

### Common Pitfalls to Avoid
1. **Using simplified format** instead of matching existing digests
2. **Missing creature details** - always describe appearance and abilities
3. **Vague motivations** - be specific (not "divine mission" but "following carved line on statue")
4. **Generic descriptions** - include specific details from roleplay
5. **Overlooking unique elements** - note special creatures, weapons, abilities
6. **Compressing roleplay** - losing personality and flavor
7. **Omitting failed attempts** - comedy and failures are part of story
8. **Wrong player mappings** - verify Erv→Qotal, Kent→Alrik, Michael→Bruldin, Katie→Aurelia, Matt→Arnor

### When Errors Are Found
If user identifies errors:
1. Accept correction immediately
2. Check for related errors (if one name wrong, verify all)
3. Update systematically (every instance, not just one)
4. Learn the pattern (transcription errors repeat)
5. Document in Technical Notes

## Output

After creating digest:
1. Report filename: "Digest for YYYY-MM-DD complete and saved to entities/notes/"
2. Note significant name resolutions made
3. List any unresolved ambiguities
4. Provide brief summary of main plot developments
5. Note number of entities captured
6. State if more unprocessed transcripts remain

Begin by finding the first unprocessed transcript and processing only that one.
