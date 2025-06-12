# Teghrim Campaign Management System

## Overview

This repository contains an AI-powered pipeline for managing tabletop RPG campaigns, specifically designed for the Teghrim campaign setting. It automates the transformation of game session audio recordings into structured, searchable campaign knowledge.

## What This Does

1. **Transcribes** game session audio recordings using AI
2. **Processes** verbose transcripts into structured session digests
3. **Generates** various content formats (narratives, summaries, podcasts)
4. **Maintains** a searchable knowledge base of all campaign entities
5. **Syncs** with Kanka.io for collaborative campaign management

## Project Structure

```
teghrim/
├── audio/                 # Raw session recordings (MP3 files)
├── transcripts/          # AI-generated session transcripts
├── entities/             # Local copies of all campaign entities
│   ├── characters/       # NPCs, deities, and notable figures
│   ├── locations/        # Cities, regions, and landmarks
│   ├── organizations/    # Factions, guilds, and groups
│   ├── races/           # Playable species and cultures
│   └── creatures/       # Monster types and animals
├── references/          # Campaign setting PDFs and source materials
├── scripts/             # Python automation scripts
└── docs/               # Documentation for various processes
```

## The Campaign Setting

Teghrim is a rich fantasy world featuring:
- Multiple pantheons of deities drawn from various mythologies
- Diverse races and cultures across several continents
- Complex political and religious organizations
- A deep history spanning multiple ages

## Key Features

### Audio Processing Pipeline
- Automated transcription of game sessions
- Speaker diarization to identify who's talking
- Conversion of transcripts into structured knowledge

### Entity Management
- Local markdown files for every campaign entity
- YAML frontmatter for metadata (tags, types, IDs)
- Bidirectional sync with Kanka.io
- Full-text search across all entities

### Content Generation
- Narrative prose from session events
- Audiobook generation with AI voices
- Podcast-style recaps with multiple speakers
- Visual scene generation from descriptions

## Getting Started

### Prerequisites
- Python 3.8+
- ffmpeg (for audio processing)
- API keys for:
  - ElevenLabs (audio generation)
  - OpenAI (transcription and image generation)
  - Kanka.io (campaign management)

### Installation
```bash
# Install Python dependencies
pip install -r scripts/requirements.txt

# Install system dependencies
# Linux:
sudo apt-get install ffmpeg
# macOS:
brew install ffmpeg
```

### Basic Usage

1. **Transcribe a session**:
   ```bash
   python scripts/transcribe_audio.py
   ```

2. **Generate an audiobook**:
   ```bash
   python scripts/generate_audiobook.py narrative.txt -o output.mp3
   ```

3. **Create session images**:
   ```bash
   python scripts/generate_image.py prompt.txt -o scene.png
   ```

## Entity Files

Each entity is stored as a markdown file with frontmatter:

```yaml
---
entity_id: 7745243      # Kanka ID (if synced)
type: Deity            # Custom type field
tags: [Demigod]        # Categorization tags
is_private: false      # Visibility setting
---

# Entity Name

Content describing the entity...
```

### Posts (Entity Notes)

Additional notes and updates for entities are stored in subdirectories:

```
entities/
  characters/
    moradin.md                          # Main entity file
    moradin/
      secret-of-eternal-flame.md        # Post file
      forging-first-hammer.md           # Another post
```

Each post file has its own frontmatter:

```yaml
---
post_id: 456           # Kanka post ID (added after sync)
entity_id: 7745243     # Parent entity's ID
title: "Secret of the Eternal Flame"
is_private: true       # GM-only visibility
created: 2025-01-06
---

Post content here...
```

## Documentation

See the `docs/` directory for detailed guides on:
- Audio transcription process
- Content generation workflows
- Kanka integration details
- Image and podcast generation

## Contributing

This is a personal campaign management system, but the structure and scripts may be useful as a template for other campaigns. Feel free to fork and adapt!

## License

The code and scripts in this repository are available for reuse. The campaign setting content (entities, references, and world-building materials) remains the intellectual property of the campaign creators.