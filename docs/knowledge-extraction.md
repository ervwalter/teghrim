# Campaign Knowledge Extraction

## Purpose

Extract structured information from session digests to maintain an authoritative, searchable database of campaign entities, relationships, and world state. This knowledge base supports consistency across sessions and enables quick reference during play.

## Input

- **Primary**: Finalized session digests with resolved entity names
- **Context**: Existing campaign knowledge base
- **Temporal**: Session date for chronological tracking

## Process

### 1. Entity Identification

Extract and categorize all mentioned entities:

**Characters**
- Player Characters (PCs)
- Non-Player Characters (NPCs)
- Mentioned individuals
- Deceased characters

**Locations**
- Settlements (cities, towns, villages)
- Buildings (taverns, shops, temples)
- Regions (kingdoms, provinces)
- Geographic features (rivers, mountains)

**Organizations**
- Formal groups (guilds, governments)
- Informal alliances
- Religious orders
- Criminal networks

**Items**
- Equipment and weapons
- Magical artifacts
- Trade goods
- Plot-relevant objects

**Events**
- Battles and conflicts
- Political changes
- Natural disasters
- Prophecies and omens

### 2. Information Extraction

For each entity, capture:

**Universal Attributes**
- Canonical name and aliases
- First appearance (session/date)
- Last seen (session/date)
- Current status (active/dead/missing)
- Brief description

**Type-Specific Details**

*Characters*:
- Race/ancestry
- Class/profession
- Affiliations
- Notable abilities
- Relationships
- Motivations

*Locations*:
- Parent location
- Population
- Government type
- Notable features
- Important residents
- Economic focus

*Organizations*:
- Leadership structure
- Members
- Goals/purpose
- Resources
- Territories
- Rivals/allies

*Items*:
- Current owner
- Previous owners
- Magical properties
- Value/rarity
- Origin/creator
- Plot significance

### 3. Relationship Mapping

Create connections between entities:
- Character → Organization membership
- Character → Location residence
- Character → Character relationships
- Location → Location hierarchy
- Organization → Location headquarters
- Item → Character ownership

### 4. Temporal Updates

Track changes over time:
- Status changes (alive → dead)
- Location movements
- Ownership transfers
- Alliance shifts
- Power dynamics
- Quest progress

### 5. Knowledge Synthesis

Update broader campaign knowledge:

**World State**
- Political situations
- Economic conditions
- Military conflicts
- Environmental changes
- Magical phenomena

**Plot Threads**
- Active quests
- Unresolved mysteries
- Character goals
- Prophetic elements
- Recurring themes

**Party Decisions**
- Major choices made
- Consequences observed
- Promises given
- Enemies made
- Allies gained

## Output Structure

### Entity Record Example
```yaml
Name: Osanna Von Carstein
Type: Character
Subtype: NPC
Status: Active
First Appearance: Session 15 (2025-05-30)
Last Seen: Session 15 (2025-05-30)
Description: Vampire noble of House Von Carstein
Race: Vampire
Class: Noble
Affiliations:
  - House Von Carstein (member)
  - Teghrim's Crossing (property owner)
Locations:
  - Old Mansion near Teghrim's Crossing (residence)
Relationships:
  - Butler (servant, vampire)
  - The Party (cordial employer)
Notable: Purchased mansion cleared by party, gifted it to them
```

### Relationship Example
```yaml
Type: Ownership
From: The Party
To: Old Mansion
Nature: Property deed
Established: Session 15
Details: Granted by Osanna after clearing
```

### World State Update
```yaml
Category: Political
Region: Teghrim's Crossing
Update: Vampire noble establishes residence
Impact: Potential undead activity increase
Date: Astra Orpheus 8th
Significance: Medium
```

## Quality Standards

### Accuracy Requirements
- Names must match finalized digest spelling
- Dates must align with session chronology
- Relationships must be bidirectional
- Status changes must be explicit

### Completeness Checks
- All new entities catalogued
- All relationships mapped
- All status changes recorded
- All plot developments noted

### Consistency Validation
- No duplicate entities
- No conflicting information
- No orphaned relationships
- No temporal paradoxes

## Integration Patterns

### New Entity Process
1. Check for existing entry
2. Validate name variations
3. Create if truly new
4. Link relationships
5. Flag for review if uncertain

### Update Process
1. Locate existing entity
2. Compare new information
3. Resolve conflicts
4. Update attributes
5. Log changes with date

### Query Support

Enable searches like:
- "All NPCs in Teghrim's Crossing"
- "Items owned by party"
- "Organizations with evil alignment"
- "Events involving vampires"
- "Quests accepted but not completed"

## Review Mechanisms

### Automated Validation
- Name consistency across mentions
- Relationship reciprocity
- Temporal sequence logic
- Required field presence

### Manual Review
- Plot significance assessment
- Ambiguous entity resolution
- Conflicting information
- Missing context

## Storage Considerations

The knowledge base must support:
- Rapid entity lookup
- Complex relationship queries
- Temporal state tracking
- Collaborative editing
- Version history
- Access permissions

## Usage Examples

### During Play
- "What do we know about Von Carstein?"
- "Where did we last see Aelysh?"
- "What items are in our party inventory?"
- "Which NPCs are in this town?"

### Between Sessions
- "What quests are we pursuing?"
- "Which NPCs owe us favors?"
- "What did we promise to do?"
- "Where haven't we explored?"

### Campaign Planning
- "Which plot threads need resolution?"
- "What NPCs could reappear?"
- "Which locations need development?"
- "What consequences await?"

## Success Metrics

Effective knowledge extraction enables:
- Zero forgotten NPCs
- Consistent world state
- Quick reference during play
- Rich campaign history
- Player engagement with lore
- GM confidence in continuity