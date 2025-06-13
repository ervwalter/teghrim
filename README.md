# Teghrim Campaign Management System

An AI-powered pipeline for transforming tabletop RPG session recordings into structured, searchable campaign knowledge. This system automates the journey from raw audio to a comprehensive campaign database synchronized with Kanka.io.

## Overview

This is a Pathfinder 2e Remastered campaign set in the homebrew world of Septerra. The system processes game session audio through multiple AI-powered stages:

### Processing Pipeline
1. **Audio Recording** → Raw MP3 files (`session-recordings/YYMMDD_####.mp3`)
2. **Transcription** → Timestamped transcripts (`transcripts/YYYY-MM-DD.md`)
3. **Digest Creation** → Structured event logs (`entities/notes/digest-YYYY-MM-DD.md`)
4. **Entity Extraction** → Update entity files from digest information
5. **Session Summaries** → Narrative journals (`entities/journals/session-summary-YYYY-MM-DD.md`)
6. **Kanka Sync** → Bidirectional synchronization with online campaign

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

### Core Workflow Commands

```bash
# Get overview of all entities (with IDs for linking)
python scripts/get_entity_overview.py

# Process new audio files
python scripts/transcribe_audio.py

# Pull from Kanka and reconcile any conflicts
python scripts/pull_from_kanka.py
# For campaign reset scenarios, preserve local changes:
python scripts/pull_from_kanka.py --preserve-local

# Find what needs to be pushed
python scripts/find_local_changes.py

# Push changes to Kanka
python scripts/push_to_kanka.py entities/characters/moradin.md
# Or push all changes with confirmation
python scripts/push_to_kanka.py --all
```

### Content Generation Commands

```bash
# Generate audiobook from narrative text
python scripts/generate_audiobook.py narrative.txt -o output.mp3 -c 15 -t "Chapter Title"

# Generate podcast from script (requires HOST: and GUEST: labels)
python scripts/generate_podcast.py script.txt -o output.mp3

# Generate image from prompt file
python scripts/generate_image.py prompt.txt -o output.png -t "Custom Title"
```

### Slash Commands (in Claude)

For AI-assisted workflows, use these commands:
- `/project:process-audio` - Transcribe audio files
- `/project:create-digests` - Create digest from first unprocessed transcript
- `/project:update-entities` - Extract entities from first unprocessed digest
- `/project:generate-session-summaries` - Create journal entries for sessions
- `/project:pull-from-kanka` - Pull and auto-reconcile conflicts
- `/project:push-to-kanka` - Push all local changes
- `/project:add-entity-links` - Add entity cross-references

## Project Structure

```
teghrim/
├── session-recordings/ # Raw MP3 recordings (YYMMDD_####.mp3)
├── transcripts/        # Timestamped session transcripts (YYYY-MM-DD.md)
├── entities/           # Local entity database (syncs with Kanka)
│   ├── characters/     # PCs, NPCs, deities, dramatis personae
│   ├── locations/      # Places, regions, landmarks
│   ├── organizations/  # Factions, guilds, governments
│   ├── races/          # Ancestries and cultures
│   ├── creatures/      # Monsters and creature types
│   ├── quests/         # Missions and objectives
│   ├── notes/          # Including digests and GM notes
│   └── journals/       # Including session summaries
├── .claude/            
│   └── commands/       # Slash command implementations
├── references/         # Campaign setting PDFs
├── scripts/            # Python automation tools
└── docs/               # Process documentation
```

## Entity Management

The system maintains a local markdown database that syncs bidirectionally with Kanka.io:

### Entity File Structure
```yaml
---
name: Moradin
entity_id: 123456    # Kanka ID (absent until first push)
type: Deity          # Specific type from metadata.json
tags: ["Greater Deity", "Dwarf Pantheon"]  # From controlled vocabulary
is_hidden: false     # true = GM only
created: '2024-12-30T10:00:00+00:00'
updated: '2024-12-31T15:30:00+00:00'
---

# Moradin

## Overview
The Forge Father and chief deity of the dwarven pantheon, Moradin represents creation, smithing, and protection.

## Description
Moradin appears as a stern-faced dwarf with a magnificent beard...

## Notable History
- **The First Forging**: Created the dwarven race from precious metals
- **The Godswar**: Led dwarven pantheon in the ancient divine conflict

## Current Status
Actively worshipped across all dwarven settlements...
```

### Entity Linking
Entities reference each other using Kanka's syntax:
- `[entity:123456]` - Link with entity's name
- `[entity:123456|custom text]` - Link with custom display text
- Link first mention per paragraph for readability

### Entity Posts
Additional notes attached to entities as separate files:
```
entities/characters/moradin/secret-of-eternal-flame.md
```

### Sync Workflow
1. **Pull**: `pull_from_kanka.py` fetches remote changes
   - Creates `.local.md` and `.kanka.md` files when conflicts exist
2. **Reconcile**: AI-assisted merge preserving content from both versions
3. **Push**: `push_to_kanka.py` uploads changes
   - Adds entity_id to new entities
   - Updates timestamps

### Writing Guidelines
- **Style**: Wikipedia-like, in-world perspective
- **Updates**: Add to history, never delete
- **Overview**: Keep current state description evergreen
- **Tags**: Use controlled vocabulary from `entities/metadata.json`
- **Special Tags**: 
  - "Major Dramatis Personae" - Key story NPCs
  - "Minor Dramatis Personae" - Supporting NPCs

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
- **`get_entity_overview.py`** - List all entities with IDs and player mappings
- **`pull_from_kanka.py`** - Sync from Kanka to local (handles pagination)
  - `--preserve-local` - Keep local changes during campaign resets
- **`push_to_kanka.py`** - Upload local changes to Kanka
  - `--all` - Push all pending changes
  - `--force-repush` - Get new IDs (for reset campaigns)
- **`find_local_changes.py`** - Identify entities needing sync
- **`clean_campaign.py`** - ⚠️ Delete all Kanka entities (use with caution)

### Utilities
- **`add_name_to_frontmatter.py`** - Bulk update entity metadata

## Campaign Setting

The Teghrim campaign is a Pathfinder 2e Remastered game set in Septerra:
- **System**: Pathfinder 2e with Remastered rules
- **Ancestries**: 42 playable options, some reskinned PF2e ancestries
- **Pantheons**: Multiple deity groups with complex relationships
- **Geography**: Multiple continents including mysterious Astoria
- **Central Hub**: Teghrim's Crossing - a massive bridge settlement
- **Organizations**: From Dwarven Slayer Cults to Goblin Raiders

## Workflows

See the `docs/` directory for detailed workflows:
- Audio transcription pipeline
- Entity sync procedures
- Campaign reset process
- Image generation guidelines
- MCP-Kanka operations

## Technical Details

### File Naming Conventions
- Audio: `YYMMDD_####.mp3` (e.g., `250530_0016.mp3`)
- Transcripts: `YYYY-MM-DD.md` (e.g., `2025-05-30.md`)
- Digests: `entities/notes/digest-YYYY-MM-DD.md`
- Summaries: `entities/journals/session-summary-YYYY-MM-DD.md`
- Entities: `entities/[type]/[name-kebab-case].md`
- Posts: `entities/[type]/[entity]/[post-title].md`

### API Constraints
- Audio files must be <2 hours for ElevenLabs API
- Speaker diarization supports up to 6 speakers
- Kanka API paginates at ~45 entities per page
- Images generated at 1536x1024 resolution

### Important Notes
- Entity IDs only exist after first Kanka push
- Always update frontmatter after creating entities/posts
- Conflicts create `.local.md` and `.kanka.md` files

## License

This project is for the Teghrim campaign. The codebase structure and scripts may be adapted for other campaigns.