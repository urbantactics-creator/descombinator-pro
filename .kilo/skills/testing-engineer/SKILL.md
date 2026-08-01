---
name: testing-engineer
description: >-
  Test strategy, test framework setup, test automation, test data management,
  and testing best practices for the Descombinator Pro project.
license: MIT
metadata:
  category: testing
  project: descombinator-pro
---

# Testing Engineer

## Responsibilities

- Design and implement comprehensive test strategy
- Set up test frameworks and tools
- Write and maintain test suites
- Manage test data and fixtures
- Implement test automation in CI/CD

## Test Strategy

### Test Pyramid

```
        E2E Tests (10%)
       /              \
Integration Tests (20%)
      /                 \
Unit Tests (70%)
```

### Test Types

| Type | Scope | Tools | Target |
|------|-------|-------|--------|
| Unit | Individual functions | pytest | 70% |
| Integration | Module interactions | pytest-asyncio | 20% |
| E2E | Full application | pytest-qt, subprocess | 10% |

## Test Framework

### pytest Configuration

```ini
# pytest.ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
qt_api = pyside6
```

### Test Markers

```python
import pytest

@pytest.mark.unit
@pytest.mark.asyncio
async def test_audio_loader():
    ...

@pytest.mark.integration
@pytest.mark.asyncio
async def test_separation_pipeline():
    ...

@pytest.mark.ui
def test_main_window(qtbot):
    ...

@pytest.mark.slow
@pytest.mark.asyncio
async def test_full_separation():
    ...
```

## Test Data Management

### Fixtures

```python
# tests/conftest.py
import pytest
from pathlib import Path

@pytest.fixture
def sample_audio_path():
    return Path("tests/fixtures/sample.wav")

@pytest.fixture
def sample_audio_data():
    return np.random.randn(44100 * 3)  # 3 seconds of audio
```

### Test Data

- Store in `tests/fixtures/`
- Use small files (< 1 MB) for fast tests
- Generate synthetic data for edge cases
- Version control test data
- Clean up after tests

## Test Automation

### CI Pipeline

```yaml
- name: Run unit tests
  run: pytest tests/unit/ --cov=engine --cov=app

- name: Run integration tests
  run: pytest tests/integration/

- name: Run UI tests
  run: pytest tests/ui/ --qt-api pyside6

- name: Run slow tests
  run: pytest tests/ -m slow
```

## Best Practices

- Write tests before implementation (TDD)
- Keep tests independent and isolated
- Use descriptive test names
- Test edge cases and error conditions
- Mock external dependencies
- Clean up after tests
- Run tests in CI on every commit
