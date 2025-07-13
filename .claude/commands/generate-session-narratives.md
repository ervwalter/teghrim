# Generate Session Narratives

This command creates narrative-style journal entries for all digests that don't already have session narratives. These are distinct from session summaries - they're written as compelling fantasy narrative chapters.

## Usage

Run this command to automatically generate session narratives for any digests that are missing them. The narratives will be created locally and can be pushed to Kanka using the push-to-kanka command.

## Process

1. Find all digest notes locally:
   ```bash
   ls entities/notes/digest-*.md | sort
   ```

2. Find existing session narratives to determine chapter numbers:
   ```bash
   ls entities/journals/session-narrative-*.md | sort
   ```
   
3. Process digests in chronological order:
   - **Process sequentially, not in parallel** - each narrative needs to read previous ones for continuity
   - For each digest that doesn't have a corresponding session narrative, launch a subagent
   - The subagent must determine the correct chapter number based on existing narratives
   - Wait for each subagent to complete before processing the next date
   - This ensures proper continuity and chapter numbering

```
Generate a session narrative for digest-YYYY-MM-DD.md

Instructions:
1. First, run `python scripts/get_entity_overview.py` to get entity names, IDs, and file paths
2. Check if `entities/journals/session-narrative-YYYY-MM-DD.md` already exists
3. If it doesn't exist:
   - Count existing session narratives to determine the chapter number:
     * List all `entities/journals/session-narrative-*.md` files
     * Sort them chronologically
     * The new narrative will be Chapter N+1
   - Find and read 2-3 session narratives from dates BEFORE YYYY-MM-DD for style and continuity
   - Read the digest from `entities/notes/digest-YYYY-MM-DD.md`
   - Read the session summary from `entities/journals/session-summary-YYYY-MM-DD.md` to:
     * Better understand the flow and significance of events
     * Get a clearer picture of what happened
     * BUT DO NOT limit yourself to its interpretation - use it as context only
   - The entity overview already provides entity IDs for linking
   - Optionally read select entity files to better understand:
     * Character personalities and speaking styles
     * Location atmospheres and details
     * BUT REMEMBER: These files contain future events - only use for characterization
   - Generate a narrative chapter following the format below
   - BEFORE SAVING: Review your narrative and verify EVERY entity against the overview
   - If any entity with an ID isn't linked, add the link
   - Create the narrative as `entities/journals/session-narrative-YYYY-MM-DD.md`
4. Report completion or any issues encountered

Narrative Generation Instructions:
[Copy all content from "Narrative Generation Instructions" section through the end of this document]
```

## Narrative Generation Instructions

$arguments

You are crafting compelling narrative chapters for a Pathfinder 2e campaign, transforming session digests into engaging fantasy prose. Each digest contains:
- **Session Overview**: Date, previous session recap, key events, party status
- **Chronological Events**: Numbered entries tagged as SCENE, ACTION, DIALOGUE, COMBAT, etc.
- **Combat Summary**: Details of encounters
- **Entities**: NPCs, Locations, Quests/Tasks, Organizations
- **Unresolved Questions**: Ambiguities and unclear elements

### Key Guidelines:
- Write in past tense with limited third-person perspective
- Focus on dramatic moments and character dynamics
- Transform mechanical events into cinematic narrative
- Use rich, sensory descriptions
- Maintain the literary style of previous narratives
- **Creative License**: Like a movie adaptation of a game, prioritize narrative flow over mechanical accuracy
- Maintain the chronological order of significant events, but feel free to:
  * Combine minor scenes for flow
  * Add sensory details and atmosphere
  * Enhance dialogue and character reactions
  * Skip trivial mechanical moments
- The digest provides the skeleton; you create the living, breathing narrative

### Chapter Structure

Your narrative should flow as a cohesive story chapter:
- Open with a scene that sets tone and connects to previous events
- Develop through clear scenes with natural transitions
- Build toward meaningful story beats or revelations
- End with forward momentum while providing some resolution
- Use scene breaks (---) between major location or time shifts

### Narrative Voice and Style

Study the existing narratives to match their voice:
- **Literary fantasy prose** with evocative descriptions
- **Sensory details** that immerse readers in scenes
- **Character perspectives** that color observations
- **Dynamic action** that transforms combat into cinematic sequences
- **Emotional depth** that explores character motivations
- **World-building** woven naturally into the narrative

Example opening style:
> Golden evening spilled across the timbered bridges of Teghrim's Crossing as the caravan rolled in, the wagon wheels rattling a rhythm at the twilight edge of civilization.

### Combat Color Coding Note:
**IMPORTANT**: Digests may contain color references like "red orc" or "blue scarecrow" - these are out-of-game miniature color codes for table management. **DO NOT include color designations in narratives.** Convert them to evocative descriptions:
- "red orc #2" → "the scarred orc leader" or "the larger warrior"
- "blue scarecrow" → "the straw sentinel" or "another construct"
- Use atmospheric, descriptive, or contextual references that enhance the narrative

### Game Mechanics Transformation:
**CRITICAL**: Never reference game mechanics directly in narratives. Transform all mechanical elements into cinematic prose:
- **Damage numbers**: "20 points of damage" → "a crushing blow that left him reeling"
- **Hit points**: "reduced to 2 hit points" → "barely clinging to life"
- **Actions**: "three-action heal" → "channeled divine power in a desperate prayer"
- **Conditions**: "clumsy 1 condition" → "fumbling with uncharacteristic clumsiness"
- **Rolls/Saves**: "failed the save" → "succumbed to the creature's influence"
- **Critical hits**: "critical hit for 38 damage" → "a bone-crushing blow that sent her sprawling"

Focus on the **narrative effect** rather than the mechanical cause. Describe what characters see, feel, and experience - not the numbers or systems behind it.

### Processing the Digest:

1. **Determine Chapter Number**:
   - List all existing `session-narrative-*.md` files
   - Count them in chronological order
   - Your narrative is the next chapter in sequence

2. **Review previous narratives** for:
   - Writing style and voice
   - Ongoing character arcs
   - Narrative threads to continue
   - The emotional tone of recent events

3. **Read the session summary** to:
   - Understand the overall story arc
   - Identify key dramatic beats
   - Get clarity on confusing digest entries
   - BUT remember: you're writing literature, not a summary recap

4. **Transform digest entries** into narrative:
   - SCENE tags become setting descriptions
   - DIALOGUE becomes character conversations (feel free to enhance/rewrite for narrative flow)
   - COMBAT becomes dynamic action sequences
   - NPC/LOCATION tags add world details
   - DISCOVERY/LORE becomes moments of revelation
   - **Adapt thoughtfully**: Combine related minor events, skip trivial moments, but preserve the chronological order of significant happenings

5. **Character perspective shifts**:
   - Focus on one viewpoint per scene
   - Shift naturally between characters
   - Use their thoughts and observations to add depth
   - Add internal monologue and emotional reactions

6. **Creative adaptation** (while maintaining chronological order):
   - Like adapting a game to film, prioritize story over mechanics
   - Add sensory details, weather, atmosphere
   - Create smooth transitions between scenes
   - Build tension and pacing through description and character reactions
   - Small talk can become meaningful dialogue
   - Failed attempts can be downplayed or described more dramatically
   - Minor scenes can be combined if they occur in the same location/time

### Entity Linking:
- Link entities on first mention per scene/section
- Use natural display text: `[entity:7763290|the Norn wanderer]`
- Vary references for narrative flow
- Only link if entity has an ID in the overview

### Creating the Journal Entry:

1. **Filename**: `entities/journals/session-narrative-YYYY-MM-DD.md`
   - Example: `entities/journals/session-narrative-2025-05-16.md`

2. **Determine the chapter number** by counting existing narratives

3. **Create an evocative title** that:
   - Uses irony, contrast, or unexpected juxtaposition
   - Implies action, tension, or emotion rather than just describing
   - Creates questions in the reader's mind
   - Avoids bland place names or simple descriptions
   - Should feel mysterious, poetic, or slightly ominous
   - Techniques for evocative titles:
     * Ironic phrases: "Necromancer's Welcome" (hostile greeting)
     * Metaphorical pairings: "Stone Hearts and Fairy Rings" (emotional + magical)
     * Action + Mystery: "The Bridge and the Bloodline" (journey + heritage)
     * Contradictions: A peaceful word with a dangerous one
     * Double meanings: Words that work literally and figuratively
   - AVOID bland titles like:
     * "The [Place Name]" 
     * "The [Object/Person]"
     * Simple descriptive phrases
   - Instead, find the emotional core or ironic twist in the events

4. **File content**:
```markdown
---
name: [Two-digit chapter number] - [Evocative Title]
type: Session Narrative
is_hidden: false
created: '[current timestamp]'
updated: '[current timestamp]'
---

# Chapter [Number] - [Evocative Title]

[The full narrative content goes here - start with the prose after the heading]
```

Note: Use two-digit format in the frontmatter name (e.g., "01 - The Bridge and the Bloodline") for better Kanka sorting, but keep single digits in the chapter heading for readability (e.g., "Chapter 1 - The Bridge and the Bloodline").

### Writing Guidelines:

**DO:**
- Write immersive fantasy prose
- Focus on character moments and emotions
- Use vivid sensory descriptions
- Create smooth scene transitions
- Build and release tension
- Include character thoughts and motivations
- Make combat dynamic and cinematic

**DON'T:**
- Mention game mechanics, dice, or numbers
- Reference damage amounts, hit points, or conditions
- Use meta-game terminology (saves, checks, rolls, actions)
- Include player names or table talk
- List events mechanically
- Rush through important moments
- Forget to link entities with IDs

### Example Style Elements:

From existing narratives:
- "boots heavy with road dust"
- "scales glinting green in the lantern light"
- "her presence as much a comfort as a warning"
- "the wind rattled shutters as if some fey hand tried to slip inside"

### CRITICAL OUTPUT REQUIREMENTS:

When generating the narrative:
- Include the chapter heading as shown in the format
- Start the prose immediately after the heading
- End with the final paragraph of the story
- No preamble or explanation
- No meta-commentary about the process
- Pure narrative content after the required heading

## Important Notes:
- Session narratives are public (is_hidden: false) while summaries are GM-only
- Each narrative should stand alone as a compelling chapter
- Maintain consistency with established character voices
- Only include events from the digest, not future knowledge
- Chapter numbers must be sequential based on existing narratives
- The narrative transforms the digest into literary fantasy prose