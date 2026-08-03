# ADR-001: Modular Monolith Architecture

- **Status:** Accepted
- **Date:** 2026-08-02
- **Deciders:** Project Architect

## Context

Descombinator Pro is a desktop application that separates audio into vocals and instrumental tracks using AI. The application needs to be maintainable, testable, and performant while running entirely on-device.

We need to decide on the overall architectural style: monolith, microservices, or plugin-based.

## Decision

We adopt a **modular monolith** architecture with clear layer separation:

```
app/          → Presentation layer (UI, controllers, widgets)
engine/       → Processing layer (audio, demucs, inference, export)
app/services/ → Orchestration layer (pipeline coordination)
```

### Rationale

- **Single process:** Desktop application, no need for network distribution
- **Clear boundaries:** `app/` has no direct `engine/` calls; communication via `app/services/`
- **Testability:** Each layer can be tested independently with mocks
- **Performance:** No IPC overhead between layers
- **Deployment:** Single executable via PyInstaller

## Consequences

### Positive

- Simple deployment (single binary)
- Fast inter-layer communication (in-process calls)
- Clear separation of concerns
- Easy to test with mocks
- No network or IPC complexity

### Negative

- Tight coupling between layers (mitigated by service layer)
- Cannot scale layers independently (not needed for desktop app)
- Single point of failure (acceptable for desktop app)

## Alternatives Considered

- **Microservices:** Rejected — unnecessary complexity for a desktop app, no network distribution needed
- **Plugin-based:** Rejected — separation backends are fixed (Demucs, OpenUnmix), no need for runtime plugin loading
