# Podcast Generation

## Purpose

Convert podcast scripts into engaging audio conversations using multiple AI voices. Creates MP3 files that sound like a natural discussion between a host and guest about the RPG session.

## Input

- **Script File**: Text file with HOST/GUEST dialogue format
- **Location**: Any path specified on command line
- **Format**: Plain text with speaker labels

### Script Format

```
HOST: Welcome to today's episode where we'll discuss the party's arrival at Teghrim's Crossing.

GUEST: It was quite an adventure! The party had been traveling for days when they finally saw the bridge.

HOST: Tell us about this bridge. It sounds like more than just a river crossing.

GUEST: Oh absolutely! Teghrim's Crossing is essentially a small city built onto a massive stone bridge...
```

## Process

### 1. Script Parsing
- Identify HOST and GUEST speaker segments
- Preserve natural dialogue flow
- Handle multi-line speeches per speaker
- Remove empty segments

### 2. Voice Assignment
- **HOST**: Professional podcast host voice (male)
- **GUEST**: Enthusiastic storyteller voice (female)
- Consistent voice IDs for character continuity

### 3. Audio Generation
- Process each dialogue segment with appropriate voice
- Use request stitching for smooth transitions
- Maintain conversational pacing (1.05x speed)
- Apply voice settings for natural speech:
  - Stability: 0.5 (some variation)
  - Similarity: 0.75 (character consistency)
  - Speaker boost: Enabled

### 4. Audio Assembly
- Combine all segments in order
- No gaps between speakers (natural conversation flow)
- Single MP3 output file

## Technical Details

### ElevenLabs Configuration
- **Model**: eleven_multilingual_v2
- **Voices**: Pre-selected for podcast style
- **Request Stitching**: Last 3 request IDs passed for consistency
- **Chunk Handling**: Automatic for long segments

### Command Line Usage

```bash
# Basic usage
python scripts/generate_podcast.py podcast-script.txt

# Specify output file
python scripts/generate_podcast.py podcast-script.txt -o episode-15.mp3

# Use specific API key
python scripts/generate_podcast.py podcast-script.txt --api-key YOUR_KEY
```

## Output

- **Format**: MP3 audio file
- **Quality**: ElevenLabs standard output
- **Naming**: Original filename with .mp3 extension (or specified)
- **Duration**: Typically 5-15 minutes depending on script

## Quality Considerations

### Voice Consistency
- Same voice IDs used throughout project
- Request stitching maintains tone across segments
- Natural conversation rhythm preserved

### Content Flow
- No artificial pauses between speakers
- Maintains energy of live conversation
- Suitable for actual podcast publishing

### Technical Quality
- Clear audio without artifacts
- Consistent volume levels
- Professional production quality

## Common Issues

### Long Scripts
- Automatically handled via streaming
- No manual splitting required
- Progress shown during generation

### Script Formatting
- Must use HOST: and GUEST: labels
- Case insensitive (Host: or host: work)
- Continuation lines don't need labels

### API Limits
- Rate limiting handled automatically
- Long scripts may take several minutes
- Progress indicators show status

## Best Practices

### Script Writing
- Keep exchanges natural and conversational
- Balance host questions with guest storytelling
- Include reactions and interjections
- Vary sentence length for rhythm

### File Organization
- Name scripts clearly (e.g., session-15-podcast.txt)
- Keep scripts with related session files
- Output to dedicated podcast directory

### Quality Control
- Listen to full output before publishing
- Check for any audio glitches
- Verify all dialogue was included
- Ensure natural conversation flow