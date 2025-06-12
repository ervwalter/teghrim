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

### Entity Sync
```bash
# Pull entities from Kanka to local files (requires KANKA_TOKEN and KANKA_CAMPAIGN_ID)
python scripts/pull_from_kanka.py

# Find local changes that need pushing
python scripts/find_local_changes.py

# Push specific entities to Kanka
python scripts/push_to_kanka.py entities/characters/gandalf.md entities/locations/rivendell.md

# Push all local changes to Kanka (with confirmation prompt)
python scripts/push_to_kanka.py --all
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
- Races (ancestries, species, cultures)
- Creatures (monster types, animals)
- Notes (GM-only information)
- Journals (session logs, chronicles)
- Quests (missions, objectives)

### Local Entity Management
The `entities/` directory maintains a local copy of all Kanka entities for the campaign:
- **Structure**: Organized by entity type (characters/, locations/, etc.)
- **Format**: Markdown files with YAML frontmatter containing metadata
- **Frontmatter fields**:
  - `entity_id`: Kanka entity ID (absent for new entities not yet uploaded)
  - `type`: Custom type field (e.g., "Deity", "City", "Guild")
  - `tags`: Array of tags for categorization
  - `is_hidden`: Visibility setting (true = GM only)
- **Benefits**: Fast local search, version control, offline access, batch operations
- **Sync workflow**: 
  1. Pull from Kanka → Update local files
  2. Edit locally → Track changes
  3. Push to Kanka → Update entity_id in frontmatter

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