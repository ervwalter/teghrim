# Teghrim Campaign Management System

An AI-powered pipeline for transforming tabletop RPG session recordings into structured, searchable campaign knowledge. This system automates the journey from raw audio to a comprehensive campaign database.

## Overview

The Teghrim system processes game session audio through multiple AI-powered stages:
1. **Transcription** - Convert MP3 recordings to timestamped text
2. **Digest Creation** - Transform verbose transcripts into structured summaries
3. **Narrative Generation** - Create story-format retellings
4. **Knowledge Extraction** - Update campaign database with entities and relationships
5. **Content Creation** - Generate audiobooks, podcasts, and images

## Quick Start

### Prerequisites

```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Install system dependency (required for audio processing)
# Linux
apt-get install ffmpeg
# macOS
brew install ffmpeg
```

### Required API Keys

Set these environment variables:
- `ELEVEN_API_KEY` - For audio transcription and generation
- `OPENAI_API_KEY` - For image generation
- `OPENAI_ORG_ID` - OpenAI organization ID
- `KANKA_TOKEN` - For campaign database sync
- `KANKA_CAMPAIGN_ID` - Your Kanka campaign ID

### Common Commands

```bash
# Transcribe session audio
python scripts/transcribe_audio.py

# Sync entities from Kanka
python scripts/pull_from_kanka.py

# Find local changes
python scripts/find_local_changes.py

# Push changes to Kanka
python scripts/push_to_kanka.py entities/characters/moradin.md
# Or push all changes
python scripts/push_to_kanka.py --all

# Generate audiobook from text
python scripts/generate_audiobook.py narrative.txt -o output.mp3

# Generate podcast from script
python scripts/generate_podcast.py script.txt -o output.mp3

# Generate image from prompt
python scripts/generate_image.py prompt.txt -o output.png
```

## Project Structure

```
teghrim/
├── audio/              # Raw MP3 recordings (YYMMDD_####.mp3)
├── transcripts/        # AI-generated transcripts
├── entities/           # Local entity database (syncs with Kanka)
│   ├── characters/     # NPCs, deities, notable figures
│   ├── locations/      # Places, regions, landmarks
│   ├── organizations/  # Factions, guilds, groups
│   ├── races/          # Ancestries and cultures
│   └── creatures/      # Monsters and animals
├── references/         # Campaign setting PDFs
├── scripts/            # Python automation tools
└── docs/               # Process documentation
```

## Entity Management

The system maintains a local markdown database that syncs bidirectionally with Kanka.io:

### Entity Format
```yaml
---
name: Moradin
entity_id: 123456
type: Deity
tags: [dwarf-pantheon, forge, creation]
is_hidden: false
created: 2024-12-30T10:00:00Z
updated: 2024-12-31T15:30:00Z
---

# Moradin

The Forge Father, patron deity of dwarves...
```

### Entity Posts
Additional notes can be attached to entities:
```
entities/characters/moradin/secret-of-eternal-flame.md
```

### Sync Workflow
1. **Pull**: `pull_from_kanka.py` fetches remote changes
2. **Edit**: Modify local markdown files
3. **Push**: `push_to_kanka.py` uploads changes
4. **Conflict Resolution**: Manual merge when both sides change

## Scripts Reference

### Audio Processing
- **`transcribe_audio.py`** - Convert MP3 to text with speaker identification
  - Handles files >2 hours by auto-splitting
  - Groups multi-part sessions automatically
  
### Content Generation
- **`generate_audiobook.py`** - Text-to-speech audiobook creation
- **`generate_podcast.py`** - Multi-voice podcast generation
- **`generate_image.py`** - AI image generation from prompts

### Entity Management
- **`pull_from_kanka.py`** - Sync from Kanka to local
- **`push_to_kanka.py`** - Upload local changes to Kanka
- **`find_local_changes.py`** - Identify entities needing sync
- **`clean_campaign.py`** - ⚠️ Delete all Kanka entities (use with caution)

### Utilities
- **`add_name_to_frontmatter.py`** - Bulk update entity metadata

## Campaign Setting

The Teghrim campaign features:
- **42 playable ancestries** from traditional fantasy to unique creations
- **Multiple pantheons** with complex divine relationships
- **Rich geography** spanning multiple continents and planes
- **Teghrim's Crossing** - The central bridge settlement connecting realms
- **Diverse organizations** from knightly orders to shadow cults

## Workflows

See the `docs/` directory for detailed workflows:
- Audio transcription pipeline
- Entity sync procedures
- Campaign reset process
- Image generation guidelines
- MCP-Kanka operations

## Technical Notes

- Audio files must be <2 hours for ElevenLabs API
- Speaker diarization supports up to 6 speakers
- Images generated at 1536x1024 resolution
- Entity cross-references use `[entity:ID]` syntax
- Local changes tracked via file modification times

## License

This project is for the Teghrim campaign. The codebase structure and scripts may be adapted for other campaigns.