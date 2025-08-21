# Create Session Digest - Orchestrated Iterative Approach

Process raw RPG session transcripts into comprehensive digests using a two-phase approach: subagent processing followed by main agent review and user interaction.

## Overview

This command uses proper orchestration:
1. **Subagent Phase**: Creates detailed draft with ambiguity markers
2. **Main Agent Phase**: Reviews, validates, presents ambiguities to user
3. **Finalization Phase**: Applies corrections and saves final digest

## Main Agent Task Flow

### Phase 1: Setup and Subagent Launch

1. **Find First Unprocessed Transcript**
   - Use LS tool on absolute path: `/path/to/transcripts/`
   - Sort results to get chronological order
   - For each transcript YYYY-MM-DD.md, check if `entities/notes/digest-YYYY-MM-DD.md` exists
   - Select FIRST unprocessed in chronological order
   - Report to user: "Found unprocessed transcript for YYYY-MM-DD"

2. **Prepare Resources and Context**
   ```bash
   mkdir -p .digests_temp
   python scripts/get_entity_overview.py > .digests_temp/entity_overview.md
   ```
   
   **MANDATORY: Read Player Character Files**
   Use Glob tool with pattern: `*.md` and path: `entities/characters/`
   For each file that has "Player Character" or "PC" in its type field:
   - READ the full file using Read tool
   - Extract: Character name, player name, class, key abilities
   - Note: Can they cast spells? What type? What weapons?
   
   Create `.digests_temp/player_characters.md` with:
   ```
   ## Player Characters
   - **Character Name**: Player Name - Class (abilities summary)
   - **Character Name**: Player Name - Class (abilities summary)
   [Continue for all PCs found]
   
   ## Class Logic Rules
   - Divine spells: [list characters who can cast divine]
   - Arcane spells: [list characters who can cast arcane]
   - No spells: [list martial-only characters]
   ```

3. **Get Participant Information**
   Ask user with context from entity files:
   ```
   I found an unprocessed transcript for YYYY-MM-DD.
   
   Based on the campaign files, the regular players/characters are:
   [List player-character pairs found in entity files]
   
   Which players were present for this session?
   Please list player names or character names.
   ```
   Store response in `.digests_temp/participants.md`

4. **Launch Subagent for Draft Creation**
   
   Deploy first subagent with clear boundaries:
   ```
   Create a DRAFT digest with the following requirements:
   - Process the entire transcript iteratively
   - Mark ALL uncertainties with [AMBIGUITY: description]
   - Do NOT attempt to resolve ambiguities
   - Save draft to .digests_temp/draft_digest.md
   - Include summary of issues in .digests_temp/processing_notes.md
   - CRITICAL: Create .digests_temp/line_mappings.md tracking source lines for each event
   ```

5. **Launch QA Verification Subagent**
   
   Deploy second subagent for accuracy verification:
   ```
   TASK: Verify the draft digest against the source transcript
   
   INPUTS:
   - .digests_temp/draft_digest.md (digest to verify)
   - .digests_temp/line_mappings.md (which lines each event came from)
   - transcripts/YYYY-MM-DD.md (source transcript)
   
   VERIFICATION PROTOCOL:
   1. For each event in the digest:
      - Look up its source lines in line_mappings.md
      - Read those specific transcript lines
      - Verify the event accurately represents the transcript
      - Check: quotes exact, dice rolls correct, actions match
   
   2. Flag issues as:
      - [HALLUCINATION]: Event not found in stated lines
      - [MISQUOTE]: Dialogue doesn't match transcript
      - [WRONG_ROLL]: Dice result incorrect
      - [WRONG_LINES]: Event from different transcript section
   
   3. Create .digests_temp/qa_report.md:
      ```
      ## Verification Summary
      - Events checked: XXX
      - Events verified: XXX
      - Issues found: XX
      
      ## Issues Detail
      Event #23: [HALLUCINATION] - No spell cast at lines 456-460
      Event #45: [MISQUOTE] - Actual: "Let's go" not "We should leave"
      Event #67: [WRONG_ROLL] - Roll was 17 not 19
      ```
   
   4. Output:
      - Annotated digest: .digests_temp/verified_digest.md
      - QA report: .digests_temp/qa_report.md
   ```

### Phase 3: Main Agent Review and Auto-Resolution

6. **Retrieve and Analyze Verified Draft**
   - Read `.digests_temp/verified_digest.md`
   - Read `.digests_temp/qa_report.md`
   - Read `.digests_temp/processing_notes.md`
   - Extract all [AMBIGUITY] markers
   - Remove any [HALLUCINATION] flagged events

7. **Auto-Resolve Ambiguities Using Available Resources**
   
   For each ambiguity, check in order:
   
   a) **Entity Files** (use semantic search or direct lookup):
      - Name spellings: Search entities/ for correct spelling
      - Character details: Check character files for abilities
      - Location/NPC names: Verify against existing files
   
   b) **Class/Ability Logic**:
      - "Speaker X casts divine spell" → Check which present characters have divine magic
      - "Speaker Y uses martial arts" → Check which characters have those abilities
      - Rule out impossible actions based on class
   
   c) **Participant List**:
      - If player wasn't present, their character likely didn't take active actions
      - Characters can be referenced even when players are absent
   
   d) **Context Clues**:
      - Previous/next events often clarify speaker
      - Combat positioning can identify actors
      - Dialogue style may match established NPC patterns
   
   e) **Common Transcription Errors**:
      - Apply known corrections from previous sessions
      - Fix obvious phonetic mistakes

8. **Track Resolution Statistics**
   ```
   QA Issues:
   - Hallucinations removed: XX
   - Misquotes corrected: XX
   
   Ambiguities found: XXX
   Auto-resolved: XX
   - From entity files: XX
   - From class logic: XX  
   - From participant list: XX
   - From context: XX
   Still unclear: XX
   ```

### Phase 4: User Interaction

9. **Present Findings to User**
   ```
   I've processed the transcript for YYYY-MM-DD into a draft digest with XXX events.
   
   Ambiguity Resolution Summary:
   - Total ambiguities marked by processor: XXX
   - Automatically resolved: XX (using entity files, class logic, and context)
   - Remaining uncertainties: XX
   
   The digest covers:
   - [Major plot point 1]
   - [Major plot point 2]
   - [Major plot point 3]
   
   [IF there are still unresolved ambiguities:]
   I couldn't resolve these items:
   
   1. [Genuinely ambiguous item that multiple present players could have done]
   2. [Critical plot point that's unclear]
   3. [New entity name with no match in files]
   
   Would you like to clarify these, or should I proceed with my best interpretation?
   
   [IF all ambiguities were resolved:]
   I was able to resolve all ambiguities using entity files and logical deduction.
   Ready to finalize the digest.
   ```

10. **Process User Response**
   - If user provides clarifications, apply them
   - If user asks for excerpts, read relevant transcript sections
   - If user approves guesses, apply logical assumptions
   - Track all decisions made

### Phase 5: Finalization

11. **Apply Corrections**
   - Update draft with resolved ambiguities
   - Remove [AMBIGUITY] markers for resolved items
   - Keep unresolved ones with clear notes
   - Ensure consistency throughout

12. **Final Validation**
    - Re-read critical sections
    - Verify timeline flows properly
    - Check character names are consistent
    - Ensure format is clean

13. **Save Final Digest**
    - Add proper frontmatter
    - Save to `entities/notes/digest-YYYY-MM-DD.md`
    - Clean up temp files
    - Report completion to user

## Subagent Instructions

The subagent receives these specific instructions:

```
TASK: Create DRAFT digest of transcripts/YYYY-MM-DD.md

YOU ARE A SUBAGENT - you cannot interact with the user. Mark all uncertainties 
for the main agent to resolve later.

RESOURCES:
- .digests_temp/entity_overview.md (all entity names and IDs)
- .digests_temp/player_characters.md (player-character mappings and abilities)
- .digests_temp/participants.md (who was present this session)
- transcripts/YYYY-MM-DD.md (full transcript to process)

CRITICAL: Read player_characters.md FIRST to understand who's who

REQUIREMENTS:
1. Process THE ENTIRE TRANSCRIPT - DO NOT STOP EARLY
2. Process iteratively in 750-line chunks until you reach THE END
3. Use TodoWrite to track your progress through ALL chunks
4. Include ALL meaningful events (target 200+ for full session)
5. Mark EVERY uncertainty with [AMBIGUITY: description]
6. Do NOT try to resolve ambiguities - mark them ALL for main agent

CRITICAL: You MUST process the COMPLETE transcript:
- Check total line count first with `wc -l transcripts/YYYY-MM-DD.md`
- Create todos for EVERY 750-line chunk needed
- DO NOT stop until you've processed the LAST line
- If transcript is 6000 lines, you need ~8 chunks
- Your final chunk should read through to the END of the file

IMPORTANT: Your job is to extract and mark, not resolve. The main agent will handle resolution using entity files and logic. Be liberal with ambiguity markers - it's better to mark too many than too few.

ITERATIVE PROTOCOL:

1. Initialize:
   - Check transcript length: `wc -l transcripts/YYYY-MM-DD.md`
   - Calculate total chunks needed (length ÷ 750, round up)
   - Create todo list with one item per chunk:
     * Chunk 1: Lines 1-850
     * Chunk 2: Lines 700-1550 (150 overlap)
     * Chunk 3: Lines 1400-2250 (150 overlap)
     * Continue until last chunk covers final lines
   - Start timeline tracker
   - Initialize draft digest

2. Process Each Chunk:
   - Read 750 lines with overlap
   - Extract events with maximum detail
   - Track speaker mappings
   - Note timestamp progression
   - Mark ALL uncertainties
   - Update draft after each chunk

3. Ambiguity Marking:
   Mark ALL of these liberally:
   - Speaker unclear: [AMBIGUITY: Speaker 3 unknown]
   - Name variations: [AMBIGUITY: "Not-Vig" transcription]
   - Any spelling uncertainty: [AMBIGUITY: "Kingram's" spelling]
   - IC/OOC boundaries: [AMBIGUITY: Possibly OOC]
   - Timeline jumps: [AMBIGUITY: Time skip?]
   - Ability/spell names: [AMBIGUITY: Spell name unclear]
   - Character actions when speaker unknown: [AMBIGUITY: Who acted?]
   
   Remember: The main agent will resolve most of these. Your job is comprehensive extraction with uncertainty flagging.

4. Timeline and Line Tracking:
   Create .digests_temp/timeline_tracker.md:
   - Current line number
   - Last timestamp seen
   - Speaker mappings discovered
   - Scenes/breaks identified
   
   Create .digests_temp/line_mappings.md:
   ```
   Event 1: Lines 23-45
   Event 2: Lines 46-52
   Event 3: Lines 53-67
   [Continue for all events]
   ```

5. Format Requirements:
   ### [Time Range: HH:MM:SS - HH:MM:SS]
   1. **TAG**: Event details including rolls and outcomes
   2. **TAG**: Next event immediately follows
   [No blank lines between events]

6. Detail Inclusion:
   INCLUDE:
   - All dice rolls with context
   - Exact dialogue quotes
   - Combat positioning/tactics
   - Failed attempts
   - NPC personality/reactions
   - Downtime activities
   - Lore revelations

   SKIP ONLY:
   - Pure scheduling talk
   - Technical issues
   - Bathroom/food breaks

7. Character Reference:
   Common mappings (verify against actual session):
   - Erv → Qotal (monk)
   - Kent → Bruldin (cleric)
   - Katie → Aurelia (witch)
   - Michael → Arnor (skald)
   - Matt → Alrik (dwarf)

8. Output Files:
   - .digests_temp/draft_digest.md (full digest with ambiguities)
   - .digests_temp/processing_notes.md (summary of issues found)
   - .digests_temp/timeline_tracker.md (timestamp progression)
   - .digests_temp/line_mappings.md (source lines for each event)

9. Completion Verification:
   Before finishing, confirm:
   - [ ] Processed lines 1 through [final line number]
   - [ ] All todos marked complete
   - [ ] Last timestamp in digest matches end of transcript
   - [ ] Event count is reasonable (50+ per hour of session)
   
   If you haven't reached the end, CONTINUE PROCESSING

TARGET: 200+ events for 4-hour session with ALL ambiguities marked and source lines tracked
```

## Processing Notes for Subagent

The subagent should create `.digests_temp/processing_notes.md`:

```markdown
# Processing Notes for YYYY-MM-DD

## Statistics
- Lines processed: XXXX
- Events extracted: XXX
- Ambiguities marked: XX
- Time range: HH:MM:SS to HH:MM:SS

## Common Ambiguity Types Found
- Speaker attributions: XX
- Name/spelling variations: XX
- Spell/ability names: XX
- IC/OOC boundaries: XX
- Timeline uncertainties: XX

## Transcription Patterns Noticed
- Frequent variations: [list common misspellings]
- Speaker numbering changes at: [line numbers]
- Audio quality issues at: [timestamps]

## Notes for Main Agent
- Many name ambiguities likely resolvable via entity files
- Speaker ambiguities may resolve via class abilities
- Check participants.md for presence verification
```

## Main Agent Resolution Guidelines

### What to Auto-Resolve (Don't Ask User)

1. **Entity Name/Spelling Issues**:
   - Search entity files for correct spelling
   - Use semantic search if exact match fails
   - Apply known transcription error patterns

2. **Speaker Attribution via Class Logic**:
   - Spell type → caster class mapping
   - Combat abilities → martial class identification  
   - Skill usage → class specialization

3. **Participant-Based Resolution**:
   - Absent players' characters don't take active actions
   - Present players distributed among unknown speakers

4. **Context-Based Resolution**:
   - Previous/next speaker often same person
   - Combat flow indicates actor
   - Dialogue patterns match established NPCs

### What Still Needs User Input

1. **Genuinely Ambiguous Actions**:
   - Multiple present characters could perform action
   - No class/ability constraints apply
   - Context doesn't clarify

2. **Critical Plot Elements**:
   - Major story decisions unclear
   - Quest objectives ambiguous
   - Important NPC statements uncertain

3. **New Entities**:
   - Names with no match in entity files
   - Unclear if new character or transcription error

### Resolution Priority

1. Check entity files first (most authoritative)
2. Apply participant constraints
3. Use class/ability logic
4. Examine surrounding context
5. Apply transcription error patterns
6. Only then ask user if still unclear

## Benefits of Orchestration

1. **Clear Separation**: Subagent focuses on extraction, main agent on validation
2. **User Interaction**: Main agent can present findings and get clarification
3. **Quality Control**: Two-phase review catches more issues
4. **Flexibility**: Main agent can request specific re-processing if needed
5. **Transparency**: User sees what's uncertain before finalization

## Output Format

Final digest follows standard format:

```markdown
---
name: Session Digest - YYYY-MM-DD
type: Session Digest
tags: [Digest]
is_hidden: true
created: 'YYYY-MM-DDTHH:MM:SS+00:00'
updated: 'YYYY-MM-DDTHH:MM:SS+00:00'
---

# Session Digest: YYYY-MM-DD

[Standard digest format with 200+ events]
```

## Final Report to User

```
Digest for YYYY-MM-DD complete:
- Total events: XXX
- Ambiguities resolved: XX
- Time range: HH:MM:SS to HH:MM:SS
- Key developments: [brief summary]
- Saved to: entities/notes/digest-YYYY-MM-DD.md

Remaining unprocessed transcripts: X
```

Begin by finding the first unprocessed transcript.