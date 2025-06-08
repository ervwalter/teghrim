# Image Generation

## Purpose

Create AI-generated artwork from text prompts to visualize key moments from RPG sessions. Produces high-quality images suitable for campaign documentation, player handouts, or promotional materials.

## Input

- **Prompt File**: Text file containing image description
- **Formats Supported**:
  - Plain text with title
  - Markdown with header
  - JSON with structured data
- **Location**: Any path specified on command line

### Input Formats

1. **Title and prompt** (recommended):
```
The Bridge Crossing
A massive stone bridge spans a churning river at dusk, with shops and buildings built into its structure, lanterns beginning to glow in the twilight mist.
```

2. **Markdown format**:
```markdown
# The Bridge Crossing
A massive stone bridge spans a churning river at dusk, with shops and buildings built into its structure, lanterns beginning to glow in the twilight mist.
```

3. **JSON format**:
```json
{
  "title": "The Bridge Crossing",
  "prompt": "A massive stone bridge spans a churning river at dusk..."
}
```

## Process

### 1. Prompt Extraction
- Parse file to separate title and prompt
- Extract session metadata from filename if present
- Validate prompt content exists

### 2. Image Generation
- Use OpenAI DALL-E API (gpt-image-1 model)
- Generate at 1536x1024 resolution (3:2 landscape)
- Single attempt per prompt (no retries)

### 3. File Saving
- Save PNG image with descriptive filename
- Create accompanying metadata JSON
- Preserve session/index information if available

### 4. Metadata Recording
- Image title and filename
- Full prompt text used
- Session date and index (if applicable)
- Generation timestamp

## Technical Details

### OpenAI Configuration
- **Model**: gpt-image-1
- **Size**: 1536x1024 pixels
- **Format**: PNG with embedded metadata
- **Quality**: Standard DALL-E output

### Command Line Usage

```bash
# Basic usage
python scripts/generate_image.py prompt.txt

# Specify output file
python scripts/generate_image.py prompt.txt -o "bridge-crossing.png"

# Override title
python scripts/generate_image.py prompt.txt --title "Epic Bridge Scene"

# Use specific API credentials
python scripts/generate_image.py prompt.txt --api-key YOUR_KEY --org-id YOUR_ORG
```

## Output

### Image File
- **Format**: PNG
- **Resolution**: 1536x1024 (3:2 aspect ratio)
- **Naming**: Based on title or session info
- **Quality**: High-resolution AI artwork

### Metadata File
- **Format**: JSON
- **Name**: Same as image with .json extension
- **Contents**:
  ```json
  {
    "title": "The Bridge Crossing",
    "prompt": "A massive stone bridge...",
    "filename": "bridge-crossing.png",
    "session_date": "2025-05-30",
    "index": 1
  }
  ```

## File Naming Conventions

### With Session Information
If filename contains session data:
- Pattern: `image-key-events.YYYY-MM-DD-N.txt`
- Output: `image-key-events.YYYY-MM-DD-Na.png`

### Without Session Information
Based on title:
- Input: `epic-bridge-scene.txt`
- Output: `Epic Bridge Scene.png`

## Quality Considerations

### Prompt Writing
- Be specific about visual details
- Include lighting and atmosphere
- Specify artistic style if desired
- Mention key elements prominently

### Image Consistency
- Same model used throughout project
- Consistent aspect ratio
- Professional quality output
- Suitable for various uses

## Common Issues

### API Limits
- Organization ID required
- Rate limits apply
- Cost per image generation
- No automatic retries

### Prompt Challenges
- Complex scenes may simplify
- Character likenesses vary
- Specific details may be interpreted creatively
- Text in images often illegible

### File Handling
- Special characters cleaned from filenames
- Metadata preserves original prompt
- Both files saved together
- Original prompt file unchanged

## Best Practices

### Prompt Design
- Focus on one key moment
- Emphasize mood and atmosphere
- Include environmental details
- Specify time of day/lighting

### File Organization
- Keep prompts with session materials
- Output to dedicated images directory
- Preserve metadata files
- Use clear, descriptive names

### Batch Processing
- Prepare multiple prompt files
- Run sequentially
- Check outputs before sharing
- Keep successful prompts for reference

## Use Cases

Generated images perfect for:
- Session recap visuals
- Character/location references
- Campaign promotional materials
- Player handouts
- Virtual tabletop backgrounds
- Campaign wiki illustrations
- Social media posts
- Podcast/video thumbnails