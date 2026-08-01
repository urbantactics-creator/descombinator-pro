---
name: qa-automation-engineer
description: >-
  Automated testing strategy, test framework setup, test coverage, CI testing,
  and quality assurance for the Descombinator Pro application.
license: MIT
metadata:
  category: testing
  project: descombinator-pro
---

# QA Automation Engineer

## Responsibilities

- Design and implement automated testing strategy
- Set up test frameworks and tools
- Write unit, integration, and end-to-end tests
- Monitor test coverage and quality metrics
- Implement CI testing pipeline

## Testing Strategy

### Test Types

| Type | Scope | Tools |
|------|-------|-------|
| Unit Tests | Individual functions/classes | pytest |
| Integration Tests | Module interactions | pytest, pytest-asyncio |
| UI Tests | User interface behavior | pytest-qt, Playwright |
| End-to-End | Full application flow | pytest, subprocess |
| Performance Tests | Speed and resource usage | pytest-benchmark, psutil |

### Test Coverage Targets

| Layer | Target |
|-------|--------|
| Engine (audio, demucs, export) | 90% |
| App (services, controllers) | 85% |
| UI (widgets, components) | 70% |
| Overall | 85% |

## Test Structure

```
tests/
├── unit/
│   ├── test_audio_loader.py
│   ├── test_demucs_separator.py
│   ├── test_export_writer.py
│   └── test_services.py
├── integration/
│   ├── test_pipeline.py
│   ├── test_file_io.py
│   └── test_model_manager.py
├── ui/
│   ├── test_main_window.py
│   ├── test_playback_controls.py
│   └── test_file_dialog.py
└── conftest.py
```

## Test Patterns

### Unit Test Example

```python
import pytest
from engine.audio.loader import AudioLoader

@pytest.mark.asyncio
async def test_load_audio_file():
    loader = AudioLoader()
    audio = await loader.load(Path("tests/fixtures/test.wav"))
    assert audio is not None
    assert len(audio) > 0
```

### UI Test Example

```python
from pytestqt.qt_compat import qt_api

def test_play_button_click(qtbot):
    widget = AudioPlayerWidget()
    qtbot.addWidget(widget)
    qtbot.mouseClick(widget.play_button, qt_api.QtCore.Qt.LeftButton)
    assert widget.is_playing
```

## CI Testing

### Test Execution

```yaml
- name: Run tests
  run: |
    pytest tests/ --cov=app --cov=engine --cov-report=xml
    bash <(curl -s https://codecov.io/bash)
```

### Test Data

- Store test fixtures in `tests/fixtures/`
- Use small audio files (< 1 MB) for fast tests
- Generate synthetic audio for edge cases
- Mock external services (HuggingFace, file system)
