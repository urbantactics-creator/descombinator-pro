# ADR-002: Async-First Architecture

- **Status:** Accepted
- **Date:** 2026-08-02
- **Deciders:** Project Architect, Python Backend Engineer

## Context

The application performs I/O-heavy operations: audio file loading, model inference, file export, and UI updates. Blocking the UI thread would result in a poor user experience.

We need to decide on the concurrency model: synchronous, threading, or async-first.

## Decision

We adopt an **async-first** architecture:

- All I/O operations use `async def`
- Blocking operations wrapped in `asyncio.to_thread()`
- UI thread never blocked by engine operations
- `QRunnable` + `QThreadPool` for Qt integration

### Rationale

- **I/O-bound workload:** File I/O, network (model downloads), and audio processing are I/O-heavy
- **UI responsiveness:** Async operations keep the UI thread free for user interactions
- **Python ecosystem:** `aiofiles`, `asyncio`, and `async with` context managers are well-supported
- **PySide6 integration:** `QRunnable` + `QThreadPool` bridges async Python with Qt's event loop

## Consequences

### Positive

- UI remains responsive during long operations
- Clean separation between I/O and computation
- Easy to test with `pytest-asyncio`
- Consistent error handling with `try/except`

### Negative

- Learning curve for async patterns
- Debugging can be more complex
- Some libraries (e.g., `soundfile`, `librosa`) are synchronous and require `asyncio.to_thread()`

## Alternatives Considered

- **Threading:** Rejected — GIL limits true parallelism, harder to reason about
- **Multiprocessing:** Rejected — excessive overhead for I/O-bound operations
- **Synchronous:** Rejected — would block the UI thread
