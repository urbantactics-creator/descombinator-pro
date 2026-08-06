# Async-First Architecture

**Status:** Accepted
**Date:** 2026-08-02

## Context

Descombinator Pro performs many I/O-bound operations:

- Audio file loading and decoding
- Model inference (GPU/CPU)
- File export and metadata writing
- UI event handling

A synchronous architecture would block the event loop during these operations, leading to a frozen UI and poor user experience.

## Decision

Adopt an **async-first** architecture where all I/O operations use `async def`.

### Key Principles

1. **All I/O is async:** File operations, network calls, and subprocess execution use `async`/`await`
2. **No blocking calls:** Synchronous code is isolated and wrapped in thread pools if necessary
3. **Consistent patterns:** All services follow the same async interface

### Implementation

```python
class AudioLoader:
    async def load(self, path: Path) -> AudioData:
        """Load audio file asynchronously."""
        return await asyncio.to_thread(self._load_sync, path)

    def _load_sync(self, path: Path) -> AudioData:
        """Synchronous implementation run in thread pool."""
        ...
```

## Consequences

### Positive

- **Responsive UI:** The interface never freezes during long operations
- **Better resource utilization:** Async I/O overlaps with CPU work
- **Consistent patterns:** All code follows the same async conventions
- **Testability:** Async code is easier to test with `pytest-asyncio`

### Negative

- **Learning curve:** Developers must understand async Python
- **Debugging complexity:** Stack traces can be harder to follow
- **Library compatibility:** Some libraries are not async-native

## Related

- [Modular Monolith ADR](modular-monolith-adr.md)
- [Service Layer ADR](../../architecture/adr-004-service-layer.md)
