# RPG Session Processing Pipeline

## Overview

This system processes tabletop RPG session recordings through multiple stages, transforming raw audio into structured campaign knowledge. The pipeline extracts characters, locations, events, and plot developments from game sessions, organizing them into a searchable knowledge base.

## Pipeline Stages

1. **Audio Transcription** - Convert MP3 recordings to timestamped transcripts
2. **Digest Creation** - Transform verbose transcripts into detailed session digests
3. **Summary Generation** - Create concise overviews for quick reference
4. **Narrative Generation** - Produce engaging story-format accounts
5. **Knowledge Extraction** - Update structured campaign database

## Key Features

- **Entity Recognition**: Automatically identifies characters, locations, items, and organizations
- **Temporal Tracking**: Maintains chronological consistency across sessions
- **Relationship Mapping**: Tracks connections between entities
- **Collaborative Editing**: Allows manual correction of AI-generated content
- **Multi-format Output**: Generates different views for different purposes

## Document Structure

- `audio-transcription.md` - Technical details of audio processing
- `transcript-to-digest.md` - Digest creation methodology
- `session-summaries.md` - Summary generation approach
- `narrative-generation.md` - Narrative writing process
- `knowledge-extraction.md` - Structured data extraction

## Getting Started

1. Place audio files in the `audio/` directory
2. Run `python scripts/transcribe_audio.py` to generate transcripts
3. Use the Kanka MCP server with Claude to process transcripts through remaining stages

## Architecture Philosophy

The system prioritizes:
- **Accuracy**: Entity names and relationships must be correct
- **Completeness**: No important information should be lost
- **Usability**: Output should be easy to search and reference
- **Flexibility**: Support multiple output formats for different needs