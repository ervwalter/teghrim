# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an AI-powered RPG campaign management system for the Teghrim campaign. It transforms tabletop game audio recordings into structured campaign knowledge through a multi-stage pipeline: transcription → digest → narrative → knowledge base. The system maintains a bidirectional sync with Kanka.io for campaign database management.

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

### Entity Sync
```bash
# Get a quick overview of all entities (names, types, player mappings)
python scripts/get_entity_overview.py

# Pull entities from Kanka to local files (requires KANKA_TOKEN and KANKA_CAMPAIGN_ID)
python scripts/pull_from_kanka.py
# For campaign reset scenarios, preserve local changes:
python scripts/pull_from_kanka.py --preserve-local

# Find local changes that need pushing
python scripts/find_local_changes.py

# Push specific entities to Kanka
python scripts/push_to_kanka.py entities/characters/moradin.md entities/locations/tir-asleen.md

# Push all local changes to Kanka (with confirmation prompt)
python scripts/push_to_kanka.py --all

# Force re-push entities (gets new IDs, useful after campaign reset)
python scripts/push_to_kanka.py --force-repush entities/characters/moradin.md

# Clean campaign (WARNING: Deletes ALL entities from Kanka)
python scripts/clean_campaign.py
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
3. **Digest Creation** → Transforms verbose transcripts into structured session digests in `digests/` directory
4. **Entity Extraction** → Processes digests to create/update local entity files
5. **Summary/Narrative Generation** → Creates different output formats for various purposes
6. **Kanka Sync** → Pushes local entity changes to Kanka campaign database

## Slash Commands

Custom commands for common workflows:
- `/project:process-audio` - Transcribe audio files
- `/project:create-digests` - Create digest from first unprocessed transcript
- `/project:extract-entities` - Extract entities from first unprocessed digest
- `/project:reconcile-conflicts` - Handle entity sync conflicts

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
The system uses Kanka MCP server for entity management. Entity types include:
- Characters (PCs and NPCs)
- Locations (settlements, buildings, regions)
- Organizations (guilds, governments, groups)
- Items (equipment, artifacts, plot objects)
- Events (battles, political changes)
- Races (ancestries, species, cultures)
- Creatures (monster types, animals)
- Notes (GM-only information)
- Journals (session logs, chronicles)
- Quests (missions, objectives)

Note: Currently only Characters, Locations, Organizations, Races, and Creatures have local directories. Quests are tracked locally in `entities/quests/` but may need manual Kanka integration.

### Local Entity Management
The `entities/` directory maintains a local copy of all Kanka entities for the campaign:
- **Structure**: Organized by entity type (characters/, locations/, etc.)
- **Format**: Markdown files with YAML frontmatter containing metadata
- **Frontmatter fields**:
  - `name`: Entity name (required)
  - `entity_id`: Kanka entity ID (absent for new entities not yet uploaded)
  - `type`: Custom type field (e.g., "Deity", "City", "Guild") - see metadata.json
  - `tags`: Array of tags for categorization - see metadata.json
  - `is_hidden`: Visibility setting (true = GM only)
  - `created`: Creation timestamp (ISO 8601)
  - `updated`: Last update timestamp (ISO 8601)
- **Benefits**: Fast local search, version control, offline access, batch operations
- **Sync workflow**: 
  1. Pull from Kanka → Update local files
  2. Edit locally → Track changes
  3. Push to Kanka → Update entity_id in frontmatter

### Entity File Best Practices
- **Naming**: Use kebab-case for filenames (e.g., `bruldin-grimstone.md`)
- **Writing Style**: Wikipedia-style, in-world perspective, no meta-game references
- **Structure**: 
  - Overview: Current state "evergreen" summary
  - Description: Physical/personality details that define them now
  - Notable History: Chronological major events with descriptive names
  - Current Status: Where they are and what they're doing now
- **Updates**: 
  - Enhance Overview if significance changes
  - Add to Notable History for new events
  - Update Current Status to reflect latest situation
  - Never delete existing content
- **Types & Tags**: Valid values defined in `entities/metadata.json`
- **Special Tags for Characters**:
  - "Major Dramatis Personae" - Key story NPCs
  - "Minor Dramatis Personae" - Notable supporting NPCs
- **Cross-references**: Use `[entity:ID]` for Kanka links or relative paths for local links

### Entity Posts
Posts (additional notes/updates attached to entities) are stored in subdirectories:
- **Structure**: `entities/[type]/[entity-name]/[post-title].md`
- **Example**: `entities/characters/moradin/secret-of-eternal-flame.md`
- **Post frontmatter**:
  - `post_id`: Kanka post ID (absent for new posts)
  - `entity_id`: Parent entity's Kanka ID (may be absent if parent entity is also new)
  - `title`: Human-readable post title
  - `is_hidden`: Visibility setting
  - `created`: Creation timestamp
- **Naming**: Use kebab-case versions of post titles
- **Sync**: After upload, add `post_id` to frontmatter

### IMPORTANT: Post-Creation Updates
**ALWAYS** update local markdown files after creating entities or posts in Kanka:
1. After creating an entity: Add the returned `entity_id` to the frontmatter
2. After creating a post: Add the returned `post_id` to the frontmatter
3. If a post's parent entity was also just created: Update the post's `entity_id` field
4. Use the Edit or MultiEdit tools to update frontmatter without losing content

This ensures local files stay in sync and can be properly tracked for future updates.

### Entity Sync Workflow
The sync workflow uses a hybrid approach:
- **Python scripts** handle fetching, comparing, and pushing entities
- **LLM agent (you)** handles intelligent conflict resolution

When conflicts arise from `pull_from_kanka.py`:
1. Read both `.local.md` and `.kanka.md` versions
2. Understand semantic differences and preserve important content from both
3. Update the main file with merged content
4. Clean up conflict files: `rm entity.local.md entity.kanka.md`

See `docs/entity-sync-workflow.md` for detailed workflow documentation.

### Entity Cross-References
When creating content that references other entities, use Kanka's mention syntax:
- `[entity:ID]` - Creates a link to entity with that ID
- `[entity:ID|custom text]` - Link with custom display text
- Find entity IDs in the frontmatter of local entity files

### File Naming Conventions
- Audio: `YYMMDD_####.mp3` (e.g., `250530_0016.mp3`)
- Transcripts: `YYYY-MM-DD.md` (e.g., `2025-05-30.md`)
- Audiobooks: `NNN - Chapter Title.mp3` (e.g., `015 - The Bridge and the Bloodline.mp3`)
- Entities: `entities/[type]/[name-kebab-case].md` (e.g., `entities/characters/moradin.md`)
- Posts: `entities/[type]/[entity-name]/[post-title].md` (e.g., `entities/characters/moradin/secret-of-eternal-flame.md`) 

### External Dependencies

Note: The `mcp-kanka/` and `python-kanka/` directories are symbolic links to external repositories, not part of this codebase.