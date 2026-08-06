# Descombinator Pro Documentation

## Structure

| Directory | Contents |
|-----------|----------|
| `architecture/` | System architecture and Architecture Decision Records (ADRs) |
| `api/` | API reference (generated from docstrings) |
| `guides/` | User guides and tutorials |
| `development/` | Development setup, contribution guidelines, and performance tuning |
| `troubleshooting/` | Common issues and solutions |
| `license-compliance/` | License documentation for code and model weights |
| `technical-debt/` | Mypy strict debt tracker |

## Quick Links

- [User Guide](guides/user-guide.md) — Installation, usage, and feature walkthroughs
- [Development Guide](development/development.md) — Setup, workflow, and testing
- [Performance Guide](development/performance.md) — Profiling, benchmarks, and optimization
- [Troubleshooting](troubleshooting/troubleshooting.md) — Common issues and solutions
- [License Compliance](license-compliance/license-compliance.md) — License information
- [Architecture ADRs](architecture/README.md) — Architecture decision records
- [Dependency Graph](architecture/dependency-graph.md) — Module dependency graph
- [Module Contracts](architecture/module-contracts.md) — Public interface definitions
- [Mypy Strict Debt Tracker](technical-debt/mypy-strict-coverage.md) — Modules excluded from strict checking

## Architecture Overview

Descombinator Pro follows a **modular monolith** architecture with clear layer separation:

```
app/          → Presentation layer (UI, controllers, widgets)
engine/       → Processing layer (audio, demucs, inference, export)
app/services/ → Orchestration layer (pipeline coordination)
```

See [ADR-001](architecture/adr-001-modular-monolith.md) for details.

## Key Decisions

| ADR | Title | Status |
|-----|-------|--------|
| [ADR-001](architecture/adr-001-modular-monolith.md) | Modular Monolith Architecture | Accepted |
| [ADR-002](architecture/adr-002-async-first.md) | Async-First Architecture | Accepted |
| [ADR-003](architecture/adr-003-pydantic-state.md) | Pydantic Models for State Management | Accepted |
| [ADR-004](architecture/adr-004-service-layer.md) | Service Layer Orchestration | Accepted |
| [ADR-005](architecture/adr-005-separation-backends.md) | Pluggable Separation Backends | Accepted |
| [ADR-006](architecture/adr-006-benchmark-regression-gate.md) | Benchmark Regression Gate | Accepted |

## Project Status

- **Phases 1-9 complete**; **Phase 10 (Packaging)** in progress — platform icon PNG integrated into PyInstaller spec, ICO/ICNS pending SVG conversion; **Phase 11 (Documentation & Release)** in progress.
- **Tests:** 665 total = 564 unit/integration @ 87.69% coverage (gate >= 85%) + 101 UI @ 78.27% coverage (gate >= 70%).
- **CI:** fully green on run #45 (commit `094a3f9`) — `lint-and-test`, `benchmark`, and `security-audit` all succeeded. ruff clean; mypy strict clean (0 issues, 155 source files).
