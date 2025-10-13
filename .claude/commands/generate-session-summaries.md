# Generate Session Summaries

This command creates concise session summaries as local journal entries for all digests that don't already have summaries.

## Reference Examples

**Read these first to understand the target style:**
- `entities/journals/session-summary-2025-06-13.md` - Concise, story-focused
- `entities/journals/session-summary-2025-07-11.md` - Good combat section example
- `entities/journals/session-summary-2025-07-18.md` - Balanced detail level

**Key observations from these examples:**
- Combat sections are 1-3 paragraphs, not play-by-play logs
- Focus on dramatic moments and outcomes, not mechanics
- No dice rolls, initiative orders, or specific damage numbers
- Player-facing recaps, not GM notes

## Core Principles

**Purpose**: These are player-facing story recaps, not detailed combat logs or GM notes.

**Style**:
- Concise prose (think Wikipedia article, not transcript)
- Past tense, third person
- Story impact over mechanical details
- Each section should be tight—no rambling

**What to emphasize**:
- Dramatic moments and character decisions
- Plot revelations and discoveries
- Memorable tactical decisions (not every dice roll)
- Quest progression and world-building

**What to exclude**:
- Meta-game content (photography, table management, real-world times)
- Detailed mechanics (dice rolls, ACs, DCs, specific damage amounts)
- Round-by-round combat play-by-play
- Out-of-character jokes and banter
- Color coding for miniatures (convert to narrative descriptions)

## Usage

Run this command to automatically generate session summaries for any digests that are missing them.

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
   - **Process sequentially, not in parallel**
   - For each digest that doesn't have a corresponding session summary, launch a subagent
   - Wait for each subagent to complete before processing the next date

```
Generate a session summary for digest-YYYY-MM-DD.md

Instructions:
1. Run `python scripts/get_entity_overview.py` to get entity names and IDs
2. **Read reference examples** to understand the target style:
   - entities/journals/session-summary-2025-06-13.md
   - entities/journals/session-summary-2025-07-11.md
   - entities/journals/session-summary-2025-07-18.md
3. Read 2-3 previous session summaries for continuity
4. Read the digest from `entities/notes/digest-YYYY-MM-DD.md`
5. Use semantic search strategically (see guidelines below)
6. Generate summary following the format below
7. BEFORE SAVING: Verify entity linking (see appendix)
8. Create as `entities/journals/session-summary-YYYY-MM-DD.md`

Summary Generation Instructions:
[Copy all content from "Writing Guidelines" section through the end]
```

## Writing Guidelines

### Summary Structure

```markdown
# [Descriptive Session Title - max 6-7 words]

## Session Overview
2-3 sentences covering main events and accomplishments.

## Story Developments
Flowing prose organized chronologically. Paragraph breaks for distinct scenes.
**DO**: Bold important discoveries on first mention
**DON'T**: List every action, include dice rolls, mention player names

## Combat & Challenges
1-3 paragraphs summarizing significant battles in prose.
**DO**: Memorable moments, key tactical decisions, dramatic outcomes
**DON'T**: Round-by-round play-by-play, initiative orders, specific damage amounts, dice rolls, skill check mechanics, table management details (color coding), meta-game references

## Discoveries & Lore
Clear paragraphs about new world information.
**DO**: Plot revelations, world-building, investigation results
**DON'T**: Repeat story developments, include future events from entity files

## Quest Updates
Bullet list of quest progression.
**DO**: Link quest entities, note completion/progress
**DON'T**: Write paragraphs here (keep it scannable)

## Next Steps
Known immediate objectives and upcoming challenges.
**DO**: Concrete options the party discussed
**DON'T**: Speculate on events not mentioned in digest
```

### Section Length Guidelines

- **Session Overview**: 2-3 sentences
- **Story Developments**: 3-8 paragraphs (most of the content)
- **Combat & Challenges**: 1-3 paragraphs (not per-round logs!)
- **Discoveries & Lore**: 2-5 paragraphs
- **Quest Updates**: Bullet list (5-10 items typical)
- **Next Steps**: 1-2 paragraphs

### Combat Section Anti-Patterns

**NEVER include**:
- "Initiative was called, Alrik rolled 20 for 34"
- "rolled 16 (success) for 1 point toward goal"
- "Aurelia measured distance—14 inches (70 feet)"
- "The GM explained the enemy sizing system"
- "Photography was taken for accurate resumption"
- "Color-coded for table management"
- Specific AC/DC numbers unless exceptionally dramatic
- Every attack roll, movement, or action in sequence

**Instead write**:
- "The grolsch proved formidable opponents with their signature power slam attacks"
- "Aurelia's recall knowledge revealed they were weak to fire"
- "Combat paused incomplete with multiple enemies still active"

### Color Coding Conversion

Digests contain miniature color codes—convert to natural descriptions:
- "red orc #2" → "the orc leader" or "another orc warrior"
- "blue goblin archers" → "goblin archers" or "the mounted goblins"
- "Green grolsch #1" → "one of the grolsch" or "the nearest hybrid"

### Using Semantic Search

Search to **understand context**, not to add extra content:
- Search for session participants, locations, and quests mentioned
- Use `extensionFilter: [".md"]` to focus on campaign content
- **Remember**: Entity files contain future events—don't include info not in the digest
- Search helps you write better prose, not find more things to include

### Temporal Constraint

**CRITICAL**: Entity files show current state with full history. Only include information that appears in the digest itself. Entity files are for:
- Looking up entity IDs for linking
- Understanding context for better writing
- **NOT** for adding events that happened after this session

## Appendix: Entity Linking

### Quick Reference

**Link first mention in each paragraph** using format: `[entity:ID|display text]`

**Must link**: Characters, locations, organizations, races, deities, major items with IDs

**Paragraph rule**: Link first mention per paragraph (not once per document, not every mention)

**Display text**: Override for natural flow
- `[entity:7764102|the wood elf]` not just "Aelysh" repeatedly
- `[entity:7763122|the slayer cult]` for variety

### Entity ID Lookup

The entity overview provides all IDs. Before finalizing, verify:
- Is this character in the overview? → Link it
- Is this location in the overview? → Link it
- Is this organization/race/deity in the overview? → Link it

### File Creation

**Filename**: `entities/journals/session-summary-YYYY-MM-DD.md`

**Frontmatter**:
```yaml
---
name: 2025-MM-DD - Descriptive Title
type: Session Summary
is_hidden: true
created: '[current ISO timestamp]'
updated: '[current ISO timestamp]'
---
```
