---
name: python-backend-engineer
description: >-
  Python backend development, async patterns, service layer design, API design,
  and code quality standards for the Descombinator Pro engine.
license: MIT
metadata:
  category: engineering
  project: descombinator-pro
---

# Python Backend Engineer

## Responsibilities

- Implement the `engine/` and `app/services/` layers in Python 3.12+
- Write clean, typed, async Python code following PEP 8 and PEP 604
- Design service interfaces and dependency injection patterns
- Implement error handling and retry logic for I/O operations
- Write unit and integration tests

## Coding Standards

- Use `async def` for all I/O-bound operations
- Type hints on all function signatures
- Use `loguru` for structured logging
- Follow the existing module structure in `engine/` and `app/services/`
- Use `aiofiles` for async file I/O

## Key Patterns

### Service Layer Pattern

```python
class SeparationService:
    def __init__(self, demucs_agent: DemucsAgent, audio_loader: AudioLoader):
        self._demucs = demucs_agent
        self._loader = audio_loader

    async def separate(self, file_path: Path) -> SeparationResult:
        audio = await self._loader.load(file_path)
        return await self._demucs.separate(audio)
```

### Error Handling

```python
try:
    result = await self._demucs.separate(audio)
except DemucsError as e:
    logger.error(f"Separation failed: {e}")
    raise SeparationError(str(e)) from e
```

## Testing

- Use `pytest` with `pytest-asyncio` for async tests
- Mock external dependencies (file system, network)
- Test both happy path and error scenarios
- Maintain >90% code coverage for service layer
