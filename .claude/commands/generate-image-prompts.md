# Generate Image Prompts

This command creates image generation prompts based on session narratives, producing three distinct prompts per session that capture key dramatic moments.

## Usage

Run this command to automatically generate image prompts for any session narratives that don't already have them. The prompts will be created as hidden notes that can be used with image generation tools.

## Process

1. Find all session narratives:
   ```bash
   ls entities/journals/session-narrative-*.md | sort
   ```

2. Check for existing image prompts:
   ```bash
   ls entities/notes/session-image-*.md | sort
   ```
   
3. Process narratives in chronological order:
   - **Process sequentially** to maintain consistency
   - For each narrative that doesn't have corresponding image prompts, launch a subagent
   - Each subagent creates 3 separate image prompt files
   - Wait for each subagent to complete before processing the next date

```
Generate image prompts for session-narrative-YYYY-MM-DD.md

Instructions:
1. First, run `python scripts/get_entity_overview.py` to get entity names, IDs, and file paths
2. Check if image prompts already exist:
   - Look for `entities/notes/session-image-YYYY-MM-DD-1.md`
   - Look for `entities/notes/session-image-YYYY-MM-DD-2.md`
   - Look for `entities/notes/session-image-YYYY-MM-DD-3.md`
3. If any are missing:
   - Read the narrative from `entities/journals/session-narrative-YYYY-MM-DD.md`
   - Identify the 3 most visually compelling moments from the narrative
   - For each moment, read relevant entity files to get accurate physical descriptions:
     * Character appearances (race, gender, clothing, equipment)
     * Location details (architecture, atmosphere, geography)
     * Creature descriptions
   - Generate 3 separate image prompt files following the format below
   - CRITICAL: Each prompt must include accurate physical descriptions in parentheses
   - Create the prompts as `entities/notes/session-image-YYYY-MM-DD-1.md` through `-3.md`
4. Report completion or any issues encountered

Image Prompt Generation Instructions:
[Copy all content from "Image Prompt Generation Instructions" section through the end of this document]
```

## Image Prompt Generation Instructions

You are creating evocative image generation prompts based on session narratives from a Pathfinder 2e campaign. Each narrative contains rich descriptions of dramatic moments that can be translated into compelling visual prompts.

### Key Guidelines:
- Extract 3 distinct dramatic moments from the narrative
- Focus on visually compelling scenes with action, emotion, or atmosphere
- Read entity files to ensure accurate character and location descriptions
- Create prompts suitable for high-quality fantasy art generation
- Each prompt should capture a specific moment, not a general scene

### Selecting Moments:

1. **Look for peak dramatic moments**:
   - Combat climaxes
   - Emotional character interactions
   - Reveals or discoveries
   - Environmental set pieces
   - Magical or supernatural events

2. **Ensure variety**:
   - Don't pick 3 combat scenes
   - Mix character focus, action, and atmosphere
   - Include different locations if possible
   - Vary the scale (close-up vs wide shot)

3. **Read entity files for accuracy**:
   - Check character files for race, gender, appearance
   - Check location files for architectural/environmental details
   - Include these details in parentheses within the prompt

### Creating Each Prompt File:

For each of the 3 prompts, create a separate file:

**Filename**: `entities/notes/session-image-YYYY-MM-DD-N.md` (where N is 1, 2, or 3)

**File content**:
```markdown
---
name: YYYY-MM-DD Image N - [Brief Scene Description]
type: Image Prompt
is_hidden: true
created: '[current timestamp]'
updated: '[current timestamp]'
---

# [Evocative Scene Title]

## Prompt

```
[Full image generation prompt with all details, character descriptions in parentheses, artistic style notes, lighting, mood, composition, etc.]
```

## Context

[1-2 sentences explaining what's happening in this scene from the narrative, for future reference]

## Key Elements

- **Characters**: [List any characters present with their basic descriptors]
- **Location**: [Where this takes place]
- **Mood**: [The emotional tone]
- **Visual Focus**: [What should draw the eye]
```

### Prompt Writing Style:

**Structure each prompt like this**:
"Epic fantasy digital painting, [scene description with action], [character descriptions with race/gender/appearance in parentheses], [environment details], [lighting and atmosphere], [artistic style notes]. [Composition notes]."

**Example**:
"Epic fantasy digital painting, a dwarven slayer (male dwarf with scarred torso, iron-gray beard, wielding a massive warhammer) stands defiantly against three charging goblins in a torch-lit caravanserai courtyard, defensive wooden stakes visible in background, orange firelight contrasting with blue moonlight, dramatic shadows. Art style: detailed, painterly, ArtStation quality. Wide shot emphasizing the warrior's stance against multiple foes."

### Character Description Requirements:

When including characters in a scene, ALWAYS specify in parentheses:
- Race (human, elf, dwarf, etc.)
- Gender 
- Key physical features from their entity file
- Notable equipment or clothing
- Any distinctive characteristics

**Example character descriptions**:
- "(female dhampir with pale skin, dark hair, leather armor, wielding a rapier)"
- "(elderly human male with wild gray hair, wearing stained chef's apron)"
- "(green-scaled Slaan monk with bo staff, simple robes)"

### Frontmatter Naming:

Use this format for good sorting in Kanka:
- `name: YYYY-MM-DD Image 1 - [Brief Description]`
- `name: YYYY-MM-DD Image 2 - [Brief Description]`
- `name: YYYY-MM-DD Image 3 - [Brief Description]`

This ensures chronological sorting and clear identification.

### Important Notes:
- Read the narrative thoroughly to identify the most visually striking moments
- Always verify character details against their entity files
- Include specific details that make each scene unique
- Focus on moments that tell a visual story
- Avoid generic fantasy scenes - make them specific to this campaign
- Don't include game mechanics or meta-references
- Each prompt should work standalone without context
- **CRITICAL**: The actual prompt must be in a plain code block for script extraction
- Use simple triple backticks ` ``` ` without a language identifier (since it gets lost in conversion)
- The entire prompt should be in a single code block
- This format survives markdown/HTML conversions and is easily extractable by scripts

## Quality Checklist:
Before saving each prompt, verify:
- [ ] Character descriptions match entity files
- [ ] Location details are accurate
- [ ] The scene is from the narrative (not invented)
- [ ] The prompt includes artistic style guidance
- [ ] Physical descriptions are in parentheses
- [ ] The mood and atmosphere are clear
- [ ] The composition is specified