# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an RPG session processing pipeline that transforms tabletop game audio recordings into structured campaign knowledge. The system uses AI to transcribe sessions, create digests, generate narratives, and maintain a searchable knowledge base via Kanka integration.

## Common Commands

### Audio Processing
```bash
# Transcribe audio files (requires ELEVEN_API_KEY env var)
python scripts/transcribe_audio.py

# Generate audiobook from narrative text (requires ELEVEN_API_KEY)
python scripts/generate_audiobook.py narrative.txt -o output.mp3 -c 15 -t "Chapter Title"

# Generate podcast from script (requires ELEVEN_API_KEY) 
python scripts/generate_podcast.py script.txt -o output.mp3
```

### Image Generation
```bash
# Generate image from prompt file (requires OPENAI_API_KEY and OPENAI_ORG_ID)
python scripts/generate_image.py prompt_file.txt -o output.png -t "Custom Title"
```

### Dependencies
```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# System dependency for audio processing (required by pydub)
# Linux: apt-get install ffmpeg
# Mac: brew install ffmpeg
```

## Architecture & Pipeline Flow

1. **Audio Files** (`audio/`) → Raw MP3 recordings named `YYMMDD_####.mp3`
2. **Transcription** → Creates timestamped transcripts in `transcripts/` directory
3. **Digest Creation** → Transforms verbose transcripts into structured session digests via Kanka MCP
4. **Summary/Narrative Generation** → Creates different output formats for various purposes
5. **Knowledge Extraction** → Updates Kanka campaign database with entities and relationships

## Key Technical Details

### Audio Constraints
- Files must be under 2 hours for ElevenLabs API
- Multi-file sessions are automatically combined
- Speaker diarization supports up to 6 speakers

### Script Conventions
- All scripts use `#!/usr/bin/env python3` shebang
- Scripts handle missing API keys gracefully  
- Image generation expects specific prompt formats (text/markdown/JSON)
- Podcast scripts require `HOST:` and `GUEST:` speaker labels

### Kanka Integration
The system uses Kanka MCP server for stages 3-5 of the pipeline. Entity types include:
- Characters (PCs and NPCs)
- Locations (settlements, buildings, regions)
- Organizations (guilds, governments, groups)
- Items (equipment, artifacts, plot objects)
- Events (battles, political changes)

### File Naming Conventions
- Audio: `YYMMDD_####.mp3` (e.g., `250530_0016.mp3`)
- Transcripts: `YYYY-MM-DD.md` (e.g., `2025-05-30.md`)
- Audiobooks: `NNN - Chapter Title.mp3` (e.g., `015 - The Bridge and the Bloodline.mp3`)