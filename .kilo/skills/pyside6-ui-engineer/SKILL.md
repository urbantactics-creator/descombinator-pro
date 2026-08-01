---
name: pyside6-ui-engineer
description: >-
  PySide6/PyQt application development, widget design, event handling,
  layout management, and UI component architecture.
license: MIT
metadata:
  category: frontend
  project: descombinator-pro
---

# PySide6 UI Engineer

## Responsibilities

- Build the desktop UI using PySide6 (Qt for Python)
- Design reusable widgets in `app/widgets/`
- Implement layouts and responsive design in `app/ui/`
- Handle user interactions and event propagation
- Integrate UI with application state and services

## UI Architecture

```
app/ui/          → Layout definitions (QML or .ui files)
app/widgets/     → Custom reusable widgets
app/controllers/ → UI logic and state binding
```

## Key Patterns

### Widget Structure

```python
from PySide6.QtWidgets import QWidget, QVBoxLayout, QPushButton

class AudioPlayerWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        self.play_button = QPushButton("Play")
        layout.addWidget(self.play_button)
```

### Signal/Slot Pattern

- Use custom signals for inter-widget communication
- Connect UI events to controller methods
- Avoid direct service calls from widgets

### Layout Management

- Use `QVBoxLayout` and `QHBoxLayout` for flexible layouts
- Use `QSplitter` for resizable panels
- Use `QStackedWidget` for multi-step workflows
- Apply `QSizePolicy` for proper resizing behavior

## Styling

- Use Qt Style Sheets (QSS) for theming
- Support dark and light themes
- Use `QPalette` for system theme integration
- Apply consistent spacing and typography

## Threading

- Use `QThread` or `QRunnable` for background tasks
- Never block the UI thread during processing
- Use signals to update UI from worker threads
- Implement progress reporting with `QProgressBar`
