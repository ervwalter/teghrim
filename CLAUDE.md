# CLAUDE.md

This file provides conceptual guidance for understanding the Teghrim campaign management system.

## Project Overview

This is an AI-powered RPG campaign management system that transforms tabletop game sessions into structured knowledge. The core concept is maintaining a living campaign database that grows with each session while preserving the full history of how the world and characters evolve.

**Campaign Setting**: This is a Pathfinder 2e Remastered campaign with a homebrew world called Septerra. Understanding PF2e mechanics helps interpret game terms in transcripts and digests (e.g., "slayer", "hero points", "dying condition", "flanking").

## Core Concepts

### The Knowledge Pipeline
Audio recordings of game sessions flow through multiple transformation stages:
- **Transcripts**: Raw timestamped dialogue from sessions
- **Digests**: Structured extracts of all game-relevant events, organized chronologically with tagged entries
- **Entity Files**: Living documents for characters, locations, organizations, etc. that accumulate history
- **Session Summaries**: Narrative retellings suitable for players to review between sessions

### Entity-Centric Design
Everything revolves around entities - the people, places, and things that make up the campaign world. Each entity:
- Lives as a markdown file with YAML frontmatter
- Accumulates history over time (never delete, only add)
- Links to other entities using Kanka's `[entity:ID|display text]` syntax
- Syncs bidirectionally with Kanka.io for online campaign management

## Entity Management Philosophy

### Local Files as Source of Truth
The `entities/` directory contains the authoritative version of all campaign content:
- Organized by type: `characters/`, `locations/`, `organizations/`, etc.
- Each entity is a markdown file with YAML frontmatter
- Files use kebab-case naming: `bruldin-grimstone.md`
- Bidirectional sync with Kanka maintains consistency

### Entity File Structure
```yaml
---
name: Entity Name
entity_id: 1234567  # Kanka ID, absent for new entities
type: Specific Type  # e.g., "City", "Deity", "Player Character"
tags: ["tag1", "tag2"]  # From controlled vocabulary
is_hidden: false  # true = GM only
created: '2025-01-01T00:00:00+00:00'
updated: '2025-01-01T00:00:00+00:00'
---

# Entity Name

## Overview
Current state summary - the "evergreen" description

## Description  
Physical appearance, personality, defining characteristics

## Notable History
- **Event Name**: What happened and when
- **Another Event**: More history (chronological order)

## Current Status
Where they are now and what they're doing

## Secrets & Mysteries
GM-only information if is_hidden: true
```

### Writing Principles
- **Wikipedia-style**: In-world perspective, no meta-game references
- **Accumulative**: Never delete content, only add new information
- **Evergreen Overview**: Keep the Overview section current
- **Chronological History**: Add events as they happen
- **Cross-linked**: Use `[entity:ID|display text]` to connect entities

### Entity Linking Rules
- Link first mention of each entity **per paragraph**
- Use natural display text: `[entity:7763290|the Norn wanderer]`
- Entity IDs found in frontmatter or via `scripts/get_entity_overview.py`

### Special Entity Types

**Digests** (`entities/notes/digest-YYYY-MM-DD.md`):
- Structured extraction from session transcripts
- Tagged chronological events (SCENE, ACTION, DIALOGUE, COMBAT, etc.)
- Source material for entity updates and session summaries

**Session Summaries** (`entities/journals/session-summary-YYYY-MM-DD.md`):
- Narrative retellings of game sessions
- Player-facing documents
- Generated from digests with entity context

**Player Characters**:
- Tracked in `entities/notes/players.md` for player-to-character mapping
- Special handling in overview scripts

## Temporal Considerations

When working with campaign content, remember:
- Entity files show the "current" state with full history
- Digests capture what happened in a specific session
- Session summaries should only include information known at that point in time
- Never include future events when processing historical sessions

## The Sync Philosophy

Local files and Kanka work together:
- Local: Fast editing, version control, bulk operations
- Kanka: Online access, player viewing, relationship visualization
- Conflicts resolved intelligently, preserving content from both sources
- Entity IDs connect the two systems