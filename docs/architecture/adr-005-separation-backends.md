# ADR-005: Pluggable Separation Backends

- **Status:** Accepted
- **Date:** 2026-08-02
- **Deciders:** AI/ML Engineer, Audio Separation Specialist

## Context

The application supports multiple separation backends: Demucs (htdemucs_ft, mdx_extra) and Open-Unmix (umxhq). We need a way to switch between backends and add new ones without modifying the core separation logic.

## Decision

We use a **protocol-based plugin pattern** with a `ModelManager` factory:

```python
class SeparationModel(Protocol):
    async def initialize(self) -> None: ...
    async def separate(self, audio: torch.Tensor) -> dict[str, torch.Tensor]: ...
    @property
    def sources(self) -> list[str]: ...

class ModelManager:
    def _create_model(self, name: str) -> SeparationModel:
        if name in (ModelName.HTDEMUCS_FT.value, ModelName.MDX_EXTRA.value):
            return DemucsAgent(config)
        elif name == ModelName.UMXHQ.value:
            return OpenUnmixAgent(config)
```

### Rationale

- **Protocol-based:** Both agents satisfy the `SeparationModel` protocol
- **Lazy initialization:** Models are created on-demand, not at startup
- **Cache:** `ModelManager` caches initialized models
- **Extensibility:** New backends can be added by implementing the protocol

## Consequences

### Positive

- Easy to add new separation backends
- Lazy loading reduces startup time
- Caching avoids re-initialization
- Type-safe interface via Protocol

### Negative

- Slight complexity in the factory pattern
- Protocol doesn't enforce async behavior at runtime

## Alternatives Considered

- **Inheritance:** Rejected — tight coupling, harder to test
- **Strategy pattern:** Rejected — similar to Protocol but less Pythonic
- **Entry points:** Rejected — overkill for a fixed set of backends
