---
name: application-state-manager
description: >-
  Application state management, state machine design, reactive state patterns,
  and state persistence for the Descombinator Pro desktop application.
license: MIT
metadata:
  category: architecture
  project: descombinator-pro
---

# Application State Manager

## Responsibilities

- Design and implement the application state management system
- Define state machines for processing workflows
- Implement reactive state patterns for UI binding
- Handle state persistence and restoration
- Coordinate state between UI and engine layers

## State Architecture

```
app/models/         → State data models (Pydantic)
app/controllers/    → State mutation logic
app/services/       → State persistence
```

## State Machine

### Processing Pipeline States

```
IDLE → LOADING → PREPROCESSING → SEPARATING → POSTPROCESSING → COMPLETE
  ↓                                                                   ↓
CANCELLED ←───────────────────────────────────────────────────────────┘
  ↓
IDLE
```

### State Model

```python
from enum import Enum
from pydantic import BaseModel
from pathlib import Path

class ProcessingState(str, Enum):
    IDLE = "idle"
    LOADING = "loading"
    PREPROCESSING = "preprocessing"
    SEPARATING = "separating"
    POSTPROCESSING = "postprocessing"
    COMPLETE = "complete"
    CANCELLED = "cancelled"
    ERROR = "error"

class AppState(BaseModel):
    current_file: Path | None = None
    processing_state: ProcessingState = ProcessingState.IDLE
    progress: float = 0.0
    error_message: str | None = None
    results: SeparationResult | None = None
```

## Reactive Patterns

### Observer Pattern

- UI components subscribe to state changes
- State changes trigger UI updates automatically
- Use signals/slots for Qt integration

### State Updates

```python
class StateManager:
    def __init__(self):
        self._state = AppState()
        self._subscribers: list[Callable] = []

    def update(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self._state, key, value)
        self._notify_subscribers()

    def _notify_subscribers(self):
        for subscriber in self._subscribers:
            subscriber(self._state)
```

## Persistence

- Save recent files list to config
- Restore window geometry and state
- Save user preferences (last used settings)
- Use `QSettings` for Qt-native persistence
