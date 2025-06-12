# MCP-Kanka Operations Layer Refactor - COMPLETED

## Overview
This document describes the completed refactor of the MCP-Kanka server that introduced an operations layer used by both MCP tools and external scripts. This enables direct programmatic access to Kanka operations while maintaining backward compatibility with existing MCP tools.

## Goals
1. Create a reusable operations layer for both MCP and external scripts
2. Maintain 100% backward compatibility with existing MCP tools
3. Improve type safety for external usage
4. Keep all existing tests passing without modification
5. Enable sync scripts to use the same logic as MCP tools

## Architecture

### Current Architecture
```
MCP Client → Tools (tools.py) → Service (service.py) → python-kanka → Kanka API
```

### New Architecture
```
MCP Client → Tools (tools.py) ─┐
                               ├→ Operations (operations.py) → Service → python-kanka → Kanka API
External Scripts ──────────────┘
```

## Implementation Plan

### Phase 1: Create Operations Layer (No Breaking Changes)

#### 1.1 Create operations.py Structure
Create `src/mcp_kanka/operations.py` with:
- `KankaOperations` class containing all business logic
- Typed result classes with `to_dict()` methods for MCP compatibility
- Singleton pattern matching existing service pattern

```python
# src/mcp_kanka/operations.py
from dataclasses import dataclass
from typing import Any
from .service import KankaService

@dataclass
class FindEntitiesResult:
    """Structured result for find_entities operation."""
    entities: list[dict[str, Any]]
    sync_info: dict[str, Any]
    
    def to_dict(self) -> dict[str, Any]:
        """Convert to MCP response format."""
        return {
            "entities": self.entities,
            "sync_info": self.sync_info
        }

class KankaOperations:
    """High-level operations for Kanka, used by both MCP tools and external scripts."""
    
    def __init__(self, service: KankaService | None = None):
        self.service = service or KankaService()
```

#### 1.2 Extract Logic from Tools
Move core logic from each `handle_*` function to corresponding operations methods:
- Preserve exact behavior
- Return typed results instead of dicts
- Handle all edge cases identically

#### 1.3 Update Tools to Delegate
Modify tools.py functions to:
- Create/get operations instance
- Call operations method
- Convert result to dict format
- Preserve error handling patterns

### Phase 2: Incremental Migration (One Tool at a Time)

#### Migration Order (Simplest to Most Complex)
1. **delete_entities** - Simple operation, good test case
2. **get_entities** - Basic fetch with include_posts option
3. **create_entities** - Batch operation with partial success pattern
4. **update_entities** - Similar to create, good for pattern validation
5. **check_entity_updates** - Sync-specific functionality
6. **find_entities** - Most complex with filtering and search
7. **Post operations** - Apply same patterns

#### Migration Pattern for Each Tool
```python
# Step 1: In operations.py - Extract logic
async def delete_entities(self, entity_ids: list[int]) -> list[DeleteEntityResult]:
    """Delete one or more entities."""
    # Move existing logic from handle_delete_entities
    # Return typed results
    
# Step 2: In tools.py - Update to delegate
async def handle_delete_entities(**params: Any) -> list[dict[str, Any]]:
    """MCP tool handler for delete_entities."""
    operations = get_operations()
    results = await operations.delete_entities(params["entity_ids"])
    return [r.to_dict() if hasattr(r, 'to_dict') else r for r in results]
```

### Phase 3: Testing Strategy

#### 3.1 Maintain Existing Test Coverage
- Integration tests continue calling MCP tools - no changes needed
- Unit tests for tools may need mock updates for operations instance
- All external behavior remains identical

#### 3.2 Add Operations Layer Tests
Create `tests/unit/test_operations.py`:
- Test operations methods directly
- Mock service layer
- Verify business logic
- Test error handling

#### 3.3 Verification Steps After Each Migration
1. Run existing unit tests: `make test`
2. Run integration tests if available
3. Verify no behavior changes
4. Add operations-specific tests

### Phase 4: Global Instance Management

```python
# operations.py
_operations: KankaOperations | None = None

def get_operations() -> KankaOperations:
    """Get or create the singleton operations instance."""
    global _operations
    if _operations is None:
        _operations = KankaOperations()
    return _operations

def create_operations(service: KankaService | None = None) -> KankaOperations:
    """Create a new operations instance for external use."""
    return KankaOperations(service)
```

### Phase 5: Error Handling

Define operations-specific exceptions:
```python
class KankaOperationsError(Exception):
    """Base exception for operations layer."""
    pass

class PartialSuccessError(KankaOperationsError):
    """Some operations succeeded, some failed."""
    def __init__(self, successes: list, failures: list):
        self.successes = successes
        self.failures = failures
```

## Implementation Checklist (All Completed)

- [x] Create operations.py with base structure
- [x] Migrate delete_entities (simplest case)
- [x] Run tests to verify no regression
- [x] Migrate get_entities
- [x] Migrate create_entities (test partial success)
- [x] Migrate update_entities
- [x] Migrate check_entity_updates
- [x] Migrate find_entities (most complex)
- [x] Migrate all post operations (create_posts, update_posts, delete_posts)
- [x] Add comprehensive operations unit tests (23 tests added)
- [x] Update __init__.py exports
- [x] Update documentation (CLAUDE.md and README.md)
- [x] Run full test suite: `make check` (all 147 tests passing)

## Usage Examples

### MCP Tools (No Change)
```python
# Existing MCP usage continues to work identically
result = await handle_find_entities(
    entity_type="character",
    name="Moradin"
)
```

### External Script Usage (New)
```python
from mcp_kanka.operations import create_operations

# Create operations instance
ops = create_operations()

# Use typed methods directly
result = await ops.find_entities(
    entity_type="character",
    name="Moradin",
    last_synced="2025-01-06T10:00:00Z"
)

# Access typed results
for entity in result.entities:
    print(f"Found: {entity['name']}")
```

### Sync Script Example
```python
from mcp_kanka.operations import create_operations

class KankaSyncManager:
    def __init__(self):
        self.ops = create_operations()
    
    async def sync_entities(self, last_sync_time: str):
        # Use operations for all Kanka interaction
        result = await self.ops.find_entities(
            last_synced=last_sync_time,
            include_full=True,
            limit=0  # Get all
        )
        
        # Process results with proper types
        return result.entities, result.sync_info
```

## Success Criteria (All Met ✅)

1. ✅ All existing tests pass without modification (124 tests)
2. ✅ MCP tools behavior is 100% identical
3. ✅ External scripts can use operations directly
4. ✅ Type safety for external usage
5. ✅ No breaking changes to public API
6. ✅ Code is more maintainable with single source of truth

## Risks and Mitigations

### Risk: Breaking existing functionality
**Mitigation**: Incremental migration with testing after each step

### Risk: Type mismatches between layers
**Mitigation**: Use `.to_dict()` pattern for MCP compatibility

### Risk: Complex error handling differences
**Mitigation**: Preserve exact error patterns in tools layer

## Notes

- The operations layer is internal to the package initially
- Can be made public API in future version if needed
- Consider async context managers for resource cleanup
- May want to add connection pooling in future