# Repository Guidelines

## Project Structure & Module Organization
- `session-recordings/`: Raw MP3 inputs (`YYMMDD_####.mp3`).
- `transcripts/`: Timestamped transcripts (`YYYY-MM-DD.md`).
- `entities/`: Canonical campaign knowledge (syncs with Kanka). Key folders: `characters/`, `locations/`, `organizations/`, `quests/`, `notes/` (digests, prompts), `journals/` (session narratives/summaries).
- `scripts/`: Operator tools for transcription, entity sync, and media generation.
- `.claude/commands/`: AI-assisted workflows (slash-command playbooks).
- Media symlinks: `images/`, `audiobooks/`, `videos/` point to external storage.

## Content Workflow & Commands
- Install deps: `pip install -r scripts/requirements.txt` (requires `ffmpeg`).
- Transcribe audio: `python scripts/transcribe_audio.py` → updates `transcripts/`.
- Create digests/narratives: follow `.claude/commands/*` playbooks; outputs land in `entities/notes/` and `entities/journals/`.
- Sync from Kanka: `python scripts/pull_from_kanka.py [--preserve-local]`.
- Reconcile conflicts: review `.local.md` vs `.kanka.md`; if unchanged, prefer Kanka and replace (`cp <entity>.kanka.md <entity>.md`).
- Find changes: `python scripts/find_local_changes.py`; Push: `python scripts/push_to_kanka.py <file.md>` or `--all`.
- Media: `python scripts/generate_audiobooks.py ...`, `python scripts/generate_podcast.py ...`, `python scripts/generate_images.py ...`.

## Naming & Frontmatter Conventions
- Journals: `entities/journals/session-summary-YYYY-MM-DD.md` (or narrative), Notes: `entities/notes/digest-YYYY-MM-DD.md` and `session-image-YYYY-MM-DD-N.md`.
- Entities include YAML frontmatter: `name`, `entity_id` (after first push), `type`, `tags`, `is_hidden`, timestamps.
- Do not hand-edit `entity_id` or timestamps; scripts manage them.

## Linking Guidelines
- Use Kanka syntax: `[entity:123456]` or `[entity:123456|custom text]`.
- Link the first mention per paragraph; do not self-link an entity to itself.
- Preserve existing links; use varied but accurate display text (e.g., `[entity:7763187|the Crossing]`).

## Review & Submission
- Before pushing: run `pull_from_kanka.py`, reconcile, then `find_local_changes.py` and targeted `push_to_kanka.py`.
- Commit messages: prefer content-focused summaries (e.g., `feat: add session 2025-07-18 digest and narrative`, `entities: updated`).
- PRs should note: purpose, affected folders, commands used, any media generated, and relevant env vars.

## Security & Configuration
- Env vars: `ELEVEN_API_KEY`, `OPENAI_API_KEY`, `OPENAI_ORG_ID`, `KANKA_TOKEN`, `KANKA_CAMPAIGN_ID` (store in `.env`, never commit).
- Use `--force-repush` only when intentionally recreating entities after a Kanka reset.
