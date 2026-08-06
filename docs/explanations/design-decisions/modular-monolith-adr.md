# Modular Monolith Architecture

**Status:** Accepted
**Date:** 2026-08-02

## Context

The application needs a clear structure that:

- Separates concerns (UI, processing, business logic)
- Is easy to navigate and maintain
- Supports testing at multiple levels
- Can evolve without becoming a distributed system

## Decision

Adopt a **modular monolith** architecture with three clear layers.

### Structure

```
app/          → Presentation layer (UI, controllers, widgets)
engine/       → Processing layer (audio, demucs, inference, export)
app/services/ → Orchestration layer (pipeline coordination)
```

### Layer Responsibilities

| Layer | Responsibility | Dependencies |
|-------|---------------|--------------|
| `app/` | UI, user interaction, state display | `app/services/` |
| `engine/` | Audio processing, ML inference, export | None (pure Python) |
| `app/services/` | Orchestration, pipeline coordination | `app/`, `engine/` |

### Key Rules

1. **`app/` never calls `engine/` directly** — all communication goes through `app/services/`
2. **`engine/` has no UI dependencies** — pure async Python
3. **One class per file** — unless closely related
4. **Clear public APIs** — defined in `__init__.py` files

## Consequences

### Positive

- **Clear boundaries:** Easy to understand what each module does
- **Testability:** Each layer can be tested independently
- **Maintainability:** Changes are localized to specific layers
- **No distributed complexity:** Single deployment, no network calls between services

### Negative

- **Tight coupling within layers:** Modules in the same layer can depend on each other
- **Deployment as a whole:** Cannot scale layers independently
- **Potential for layer violations:** Requires discipline to maintain boundaries

## Related

- [Async-First ADR](async-first-adr.md)
- [Service Layer ADR](../../architecture/adr-004-service-layer.md)
