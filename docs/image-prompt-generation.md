# Image Prompt Generation

## Purpose

Extract key visual moments from session digests and create detailed prompts for AI image generation. This process identifies the most impactful, cinematic moments that would benefit from visual representation.

## Input

- **Source**: Finalized session digests
- **Content**: Chronological event logs with scene markers
- **Context**: Campaign setting and established visual themes

## Process

### 1. Scene Identification

Scan digest for visually compelling moments:
- **First Impressions**: New locations, important NPCs
- **Action Scenes**: Combat highlights, dramatic escapes
- **Emotional Peaks**: Character moments, revelations
- **Environmental**: Atmospheric settings, weather events
- **Magical Effects**: Spells, supernatural occurrences

### 2. Moment Selection

Choose 3-5 scenes per session based on:
- **Visual Impact**: How striking would this image be?
- **Story Importance**: Does it capture a key moment?
- **Variety**: Different types of scenes
- **Feasibility**: Can AI effectively render this?

### 3. Prompt Construction

Transform scene descriptions into detailed prompts:

#### Basic Structure
```
[Setting/Environment] [Key Action/Subject] [Atmospheric Details] [Artistic Style]
```

#### Enhancement Techniques
- **Specific Details**: Architecture, clothing, weapons
- **Lighting**: Time of day, weather, magical glow
- **Mood**: Tense, triumphant, mysterious, serene
- **Composition**: Viewpoint, focus, scale
- **Style Notes**: Fantasy art, cinematic, painterly

### 4. Title Creation

Generate evocative titles that:
- Capture the moment's essence
- Avoid spoilers
- Sound intriguing
- Work as artwork captions

## Examples

### From Digest to Prompt

**Digest Entry**:
> SCENE – The party arrives at Teghrim's Crossing, a bridge spanning the Rothehurst River, with hostels, stores, and dining areas under the command of Captain Irka Spritzel.

**Generated Prompt**:
> A massive stone bridge spans a wide, churning river at golden hour, with colorful market stalls, hanging lanterns, and multi-story buildings built directly into the bridge's structure. Medieval fantasy architecture with smoke rising from chimneys, people bustling about, and mist rising from the water below. Epic fantasy landscape painting style.

**Title**: "Teghrim's Crossing at Dusk"

---

**Digest Entry**:
> COMBAT – Fight with 6 skims at the old mansion: necromancer flees, party victorious

**Generated Prompt**:
> Dynamic combat scene in an overgrown mansion courtyard. A robed necromancer flees up stone steps while heroes battle grotesque goblin-like creatures. Spells fly through the air with crackling energy, a dwarf cleric's hammer glows with divine light. Crumbling architecture, creeping vines, late afternoon shadows. Action-packed fantasy illustration style.

**Title**: "Battle at the Ruined Manor"

## Prompt Templates

### Location Reveal
```
[Architectural description] in [environment type] during [time/weather].
[Notable features], [atmospheric elements], and [signs of life/activity].
[Color palette] with [lighting description]. [Art style] style.
```

### Combat Scene
```
[Action description] in [location]. [Primary combatants] engaged in [type of combat].
[Magical/special effects], [environmental hazards], [dramatic positioning].
[Mood adjectives] scene with [lighting]. [Art style] illustration style.
```

### Character Introduction
```
[Character description] stands in [setting], [pose/action].
[Clothing/equipment details], [distinguishing features], [expression/mood].
[Background elements] frame the scene. [Lighting] illumination.
[Art style] character portrait style.
```

### Atmospheric Scene
```
[Wide environment description] under [weather/time conditions].
[Foreground elements], [middle ground activity], [background vista].
[Natural phenomena], [color palette], [mood descriptors].
[Art style] landscape painting style.
```

## Selection Criteria

### Must Include
- Session's most pivotal moment
- Major location first appearances
- Significant NPC introductions
- Victory or defeat scenes

### Should Include
- Unique magical moments
- Environmental challenges
- Character development scenes
- Mystery revelations

### May Include
- Humorous moments (if visually interesting)
- Quiet character scenes
- Travel sequences
- Social encounters

## Quality Guidelines

### Effective Prompts Have
- **Concrete Details**: Specific, not vague
- **Visual Focus**: What to emphasize
- **Atmospheric Context**: Mood and feeling
- **Technical Clarity**: Art style and composition

### Avoid
- **Cluttered Scenes**: Too many elements
- **Abstract Concepts**: Hard to visualize
- **Spoiler Content**: Major plot reveals
- **Impossible Perspectives**: Conflicting views

## Output Format

```markdown
## Image Prompts - Session [Date]

### 1. [Title]
[Full prompt text]

### 2. [Title]
[Full prompt text]

### 3. [Title]
[Full prompt text]
```

## Workflow Integration

1. Process immediately after digest finalization
2. Review for visual potential
3. Generate 3-5 prompts per session
4. Queue for image generation
5. Match generated images to scenes

## Common Patterns

### Session Types to Prompt Ratios
- **Combat Heavy**: 2 battle, 1 location, 1 character
- **Exploration**: 2-3 locations, 1-2 atmosphere
- **Social**: 2 character, 1 location, 1 mood
- **Mystery**: 1 clue scene, 1 location, 1 revelation

### Recurring Elements
- Party group shots (limit 1 per 3 sessions)
- Villain reveals (always include)
- New location arrivals (always include)
- Magic item discoveries (if visually interesting)

## Success Metrics

Good prompt generation results in:
- Images players want to share
- Scenes players remember
- Usable campaign assets
- Consistent visual style
- Minimal generation failures