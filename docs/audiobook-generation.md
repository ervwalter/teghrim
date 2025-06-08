# Audiobook Generation

## Purpose

Transform narrative text into professional audiobook recordings with chapter announcements. Creates immersive audio versions of session stories that can be enjoyed like traditional fantasy audiobooks.

## Input

- **Narrative File**: Markdown or text file with story content
- **Chapter Info**: Extracted from file or provided via command line
- **Format**: Plain text with optional markdown formatting

### Expected Formats

1. **Markdown with chapter header**:
```markdown
# Chapter 15: The Bridge and the Bloodline

The morning mist clung to the Rothehurst River as the party crested the final hill...
```

2. **Plain text with title**:
```
Chapter 15: The Bridge and the Bloodline

The morning mist clung to the Rothehurst River as the party crested the final hill...
```

3. **Filename-based** (fallback):
- `chapter-15-bridge-bloodline.txt`
- `15-bridge-bloodline.md`

## Process

### 1. Text Preparation
- Extract chapter number and title
- Strip markdown formatting (bold, italic, links)
- Remove headers and horizontal rules
- Clean up excessive line breaks
- Prepend chapter announcement

### 2. Chapter Announcement
Every audiobook begins with:
```
"Chapter [Number]: [Title]..."
[pause]
[narrative begins]
```

### 3. Text Chunking
- Split at sentence boundaries for long texts
- Maximum 3000 characters per chunk
- Preserve paragraph structure
- Maintain narrative flow

### 4. Audio Generation
- Professional narrator voice (Callum)
- Consistent pacing (1.05x speed)
- Natural speech patterns
- Request stitching for multi-chunk consistency

### 5. Audio Assembly
- Seamless combination of chunks
- No audible breaks in narration
- Single MP3 output

## Technical Details

### Voice Configuration
- **Voice ID**: Professional male narrator
- **Model**: eleven_multilingual_v2
- **Settings**:
  - Stability: 0.5
  - Similarity: 0.75
  - Speaker Boost: Enabled
  - Speed: 1.05x

### Command Line Usage

```bash
# Basic usage (auto-detects chapter info)
python scripts/generate_audiobook.py narrative.txt

# Specify output file
python scripts/generate_audiobook.py narrative.txt -o "Chapter 15.mp3"

# Override chapter info
python scripts/generate_audiobook.py narrative.txt --chapter 15 --title "The Bridge and the Bloodline"

# Use specific API key
python scripts/generate_audiobook.py narrative.txt --api-key YOUR_KEY
```

## Output

- **Format**: MP3 audio file
- **Naming**: `NNN - Title.mp3` (e.g., `015 - The Bridge and the Bloodline.mp3`)
- **Quality**: Professional audiobook standard
- **Duration**: Varies by text length (typically 10-30 minutes)

## File Naming Convention

Output files follow audiobook standards:
- Three-digit chapter number (zero-padded)
- Separator dash with spaces
- Clean, filesystem-safe title
- `.mp3` extension

Examples:
- `001 - The Adventure Begins.mp3`
- `015 - The Bridge and the Bloodline.mp3`
- `023 - Vampire Negotiations.mp3`

## Quality Considerations

### Narration Style
- Professional audiobook quality
- Clear, engaging delivery
- Appropriate pacing for fantasy content
- Consistent voice throughout

### Text Processing
- Preserves story flow
- Removes technical markup
- Maintains paragraph breaks
- Handles dialogue naturally

### Chapter Continuity
- Consistent narrator across all chapters
- Same audio settings maintained
- Professional introduction format
- Suitable for compilation into full audiobook

## Common Issues

### Chapter Detection
- Ensure clear chapter marking in file
- Use command line options if auto-detection fails
- Check filename follows expected patterns

### Long Chapters
- Automatic chunking handles any length
- Progress shown during generation
- May take several minutes for long texts

### Special Characters
- Fantasy names preserved correctly
- Punctuation guides narration rhythm
- Em-dashes and ellipses handled properly

## Best Practices

### File Preparation
- One chapter per file
- Clear chapter numbering
- Descriptive titles
- Clean narrative text

### Organization
- Sequential chapter numbers
- Consistent naming scheme
- Separate audiobook output directory
- Keep source narratives organized

### Quality Control
- Listen to chapter announcement
- Verify complete narration
- Check audio quality
- Ensure proper chapter sequence

## Integration Notes

Audiobooks can be:
- Combined into longer compilations
- Published to podcast platforms
- Shared with players
- Used as session recaps
- Compiled into campaign audiobook