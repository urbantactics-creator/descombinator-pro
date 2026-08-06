# Architecture Overview

Descombinator Pro follows a **modular monolith** architecture with clear layer separation.

## Layers

```
app/          → Presentation layer (UI, controllers, widgets)
engine/       → Processing layer (audio, demucs, inference, export)
app/services/ → Orchestration layer (pipeline coordination)
```

### Presentation Layer (`app/`)

- **UI:** PySide6-based desktop interface
- **Controllers:** Bind UI state to business logic
- **Widgets:** Custom reusable UI components
- **Models:** Pydantic data models for state management

### Processing Layer (`engine/`)

- **Audio:** Loading, resampling, DSP pipeline
- **Demucs:** Demucs separation backend
- **Inference:** Model inference pipeline
- **Export:** Result export and file writing
- **Performance:** Profiling, monitoring, runtime optimization

### Orchestration Layer (`app/services/`)

- Coordinates between `app/` and `engine/`
- Manages separation pipelines
- Handles async I/O and error propagation

## Key Principles

1. **Async-first:** All I/O operations use `async def`
2. **Type safety:** Modern type hints on all function signatures
3. **Separation of concerns:** Clear boundaries between layers
4. **Testability:** Each layer can be tested independently

## Module Contracts

See [Module Contracts](../../architecture/module-contracts.md) for public interface definitions.

## Dependency Graph

See [Dependency Graph](../../architecture/dependency-graph.md) for the full module dependency graph.

## Architecture Decision Records

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](../../architecture/adr-001-modular-monolith.md) | Modular Monolith Architecture | Accepted |
| [ADR-002](../../architecture/adr-002-async-first.md) | Async-First Architecture | Accepted |
| [ADR-003](../../architecture/adr-003-pydantic-state.md) | Pydantic Models for State Management | Accepted |
| [ADR-004](../../architecture/adr-004-service-layer.md) | Service Layer Orchestration | Accepted |
| [ADR-005](../../architecture/adr-005-separation-backends.md) | Pluggable Separation Backends | Accepted |
| [ADR-006](../../architecture/adr-006-benchmark-regression-gate.md) | Benchmark Regression Gate | Accepted |
