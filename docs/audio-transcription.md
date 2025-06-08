# Audio Transcription

## Purpose

Convert raw MP3 recordings of RPG sessions into timestamped, speaker-labeled transcripts that serve as the foundation for all subsequent processing.

## Input

- **Format**: MP3 audio files
- **Naming**: `YYMMDD_####.mp3` (e.g., `250530_0001.mp3`)
- **Duration**: Must be under 2 hours per file
- **Location**: `audio/` directory

## Process

### 1. File Discovery
- Scan audio directory for unprocessed sessions
- Group files by date (multiple files = single session)
- Check for existing transcripts to avoid reprocessing

### 2. Duration Validation
- Verify each file is under 2-hour limit
- Files over limit must be manually split before processing
- Prevents API timeouts and ensures quality

### 3. Transcription
- Uses ElevenLabs Speech-to-Text API
- Speaker diarization enabled (up to 6 speakers)
- Audio event tagging for non-speech sounds
- Preserves exact spoken words, including:
  - Filler words ("um", "uh")
  - False starts
  - Corrections
  - Cross-talk

### 4. Formatting
- Timestamps in `[HH:MM:SS]` format
- Speaker labels as "Speaker 1", "Speaker 2", etc.
- Paragraph breaks on speaker changes or long pauses
- File separators (`---`) for multi-file sessions

## Output

- **Format**: Markdown files
- **Naming**: `YYYY-MM-DD.md` (e.g., `2025-05-30.md`)
- **Location**: `transcripts/` directory
- **Content**: Raw, unedited transcription with all speech preserved

## Example Output

```markdown
[00:00:15] Speaker 1: Okay, so, um, last time we left off, you guys were approaching the bridge...

[00:00:23] Speaker 2: Right, right. I think my character was scouting ahead?

[00:00:28] Speaker 1: Yes, exactly. So Aurelia, you're about 30 feet ahead of the party...

---

[00:45:12] Speaker 3: Wait, can I- can I roll perception to see if there's anyone watching us?

[00:45:17] Speaker 1: Sure, go ahead and roll.

[00:45:19] Speaker 3: That's... 14 plus 3, so 17.
```

## Quality Considerations

- **Accuracy**: Generally 95%+ for clear speech
- **Speaker Attribution**: May occasionally mislabel speakers
- **Crosstalk**: Overlapping speech may be incomplete
- **Game Terms**: Fantasy names often need correction
- **Dice Sounds**: Usually tagged as [sound] or omitted

## Technical Requirements

- ElevenLabs API key (environment variable: `ELEVEN_API_KEY`)
- Python dependencies in `scripts/requirements.txt`
- System audio libraries (ffmpeg) for duration checking

## Common Issues

1. **Long Files**: Split files over 2 hours before processing
2. **Poor Audio**: Background noise reduces accuracy
3. **Many Speakers**: More than 6 people challenges diarization
4. **Technical Terms**: Game-specific vocabulary may be misheard

## Next Stage

Raw transcripts are verbose and contain all speech artifacts. The next stage (Transcript to Digest) will clean and structure this content while preserving all game-relevant information.