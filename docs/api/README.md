# API Reference

This section provides API reference documentation for Descombinator Pro's public interfaces.

## Overview

The API is organized into three layers:

1. **Engine Layer** (`engine/`) — Processing layer with no UI dependencies
2. **Service Layer** (`app/services/`) — Orchestration layer coordinating between app and engine
3. **Presentation Layer** (`app/`) — UI components, controllers, and widgets

## Documentation

- [Python API](python.md) — Auto-generated API reference from docstrings
- [Usage Guides](guides.md) — Practical examples and integration patterns

## Inline Documentation Standards

All public modules, classes, and methods follow these documentation standards:

```python
"""Module-level docstring describing the module's purpose.

Example:
    >>> loader = AudioLoader()
    >>> audio = await loader.load(Path("song.mp3"))
"""

class ClassName:
    """Class-level docstring describing the class's purpose.

    Attributes:
        attribute_name: Description of the attribute.
    """

    def method_name(self, param: type) -> return_type:
        """Method-level docstring.

        Args:
            param: Description of the parameter.

        Returns:
            Description of the return value.

        Raises:
            ExceptionType: When the exception occurs.
        """
```
