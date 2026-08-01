---
name: project-architect
description: >-
  System architecture design, module decomposition, dependency graph planning,
  and technical roadmap definition for the Descombinator Pro project.
license: MIT
metadata:
  category: architecture
  project: descombinator-pro
---

# Project Architect

## Responsibilities

- Define the overall system architecture for Descombinator Pro
- Decompose the application into cohesive, loosely-coupled modules
- Design the dependency graph between `app/` and `engine/` layers
- Plan the technical roadmap and milestone deliverables
- Ensure architectural decisions align with performance and cross-platform goals

## Key Decisions

| Decision | Options | Recommendation |
|----------|---------|----------------|
| Architecture | Monolith, Microservices, Plugin-based | Modular monolith with clear layer separation |
| Communication | Direct calls, Event bus, Message queue | Direct calls within process, event bus for UI updates |
| State Management | Global store, FSM, Reactive | FSM for processing pipeline, reactive for UI |
| Plugin System | None, Entry points, Dynamic import | Dynamic import for separation backends |

## Module Boundaries

```
app/          → Presentation layer (UI, controllers, widgets)
engine/       → Processing layer (audio, demucs, inference, export)
app/services/ → Orchestration layer (pipeline coordination)
```

## Deliverables

1. Architecture decision records (ADRs) in `docs/architecture/`
2. Dependency graph diagram
3. Module interface contracts
4. Technical roadmap aligned with product milestones
