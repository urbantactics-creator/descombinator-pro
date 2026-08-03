# ADR-004: Service Layer Orchestration

- **Status:** Accepted
- **Date:** 2026-08-02
- **Deciders:** Project Architect, Python Backend Engineer

## Context

The `app/` (presentation) and `engine/` (processing) layers need to coordinate complex workflows: audio loading → model inference → postprocessing → export. We need a pattern that keeps these layers decoupled while enabling coordination.

## Decision

We introduce a **service layer** (`app/services/`) that orchestrates between `app/` and `engine/`:

```python
class SeparationService:
    def __init__(self, demucs_agent: DemucsAgent, audio_loader: AudioLoader):
        self._demucs = demucs_agent
        self._loader = audio_loader

    async def separate(self, file_path: Path) -> SeparationResult:
        audio = await self._loader.load(file_path)
        return await self._demucs.separate(audio)
```

### Rationale

- **Dependency injection:** Services receive their dependencies, making them testable
- **Layer isolation:** `app/` never calls `engine/` directly
- **Single responsibility:** Each service handles one workflow
- **Error handling:** Services translate engine errors into app-level errors

## Consequences

### Positive

- Clear separation of concerns
- Easy to mock services in UI tests
- Centralized error handling and logging
- Reusable across different UI entry points

### Negative

- Additional layer of indirection
- More files to maintain

## Alternatives Considered

- **Direct calls:** Rejected — violates layer boundaries
- **Event bus:** Rejected — overkill for in-process communication
- **Command pattern:** Rejected — adds complexity without clear benefit
