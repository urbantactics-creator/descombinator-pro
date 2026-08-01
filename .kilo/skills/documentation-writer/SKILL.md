---
name: documentation-writer
description: >-
  Technical documentation, user guides, API documentation, inline code
  documentation, and documentation maintenance for the Descombinator Pro project.
license: MIT
metadata:
  category: documentation
  project: descombinator-pro
---

# Documentation Writer

## Responsibilities

- Write and maintain technical documentation
- Create user guides and tutorials
- Document API and architecture
- Maintain inline code documentation
- Keep documentation in sync with code changes

## Documentation Structure

```
docs/
├── architecture/       → System architecture and ADRs
├── api/                → API reference
├── guides/             → User guides and tutorials
├── development/        → Developer setup and contribution
├── troubleshooting/    → Common issues and solutions
└── license-compliance/ → License documentation
```

## Documentation Types

### User Documentation

- Installation guide
- Quick start tutorial
- Feature walkthroughs
- FAQ
- Troubleshooting guide

### Developer Documentation

- Architecture overview
- Module documentation
- API reference
- Contribution guidelines
- Testing guide

### Inline Documentation

- Module-level docstrings
- Class docstrings
- Method docstrings
- Type annotations
- Example usage in docstrings

## Documentation Standards

### Style Guide

- Use clear, concise language
- Write in active voice
- Use present tense
- Include code examples
- Link to related documentation

### Code Documentation

```python
"""Audio loader module for Descombinator Pro.

This module provides async audio file loading with format detection
and resampling capabilities.

Example:
    >>> loader = AudioLoader()
    >>> audio = await loader.load(Path("song.mp3"))
"""

class AudioLoader:
    """Load and preprocess audio files for separation.

    Supports MP3, WAV, FLAC, M4A, and OGG formats.
    Automatically resamples to the target sample rate.

    Attributes:
        target_sample_rate: Target sample rate for loaded audio.
    """

    def __init__(self, target_sample_rate: int = 44100):
        """Initialize the audio loader.

        Args:
            target_sample_rate: Sample rate to resample audio to.
        """
        self.target_sample_rate = target_sample_rate
```

## Documentation Tools

| Tool | Purpose |
|------|---------|
| Markdown | Primary documentation format |
| Sphinx | API documentation generation |
| MkDocs | Static documentation site |
| pdoc | Python API documentation |

## Maintenance

- Update documentation with every code change
- Review documentation in pull requests
- Run documentation linting
- Generate API docs from source code
