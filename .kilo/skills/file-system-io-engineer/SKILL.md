---
name: file-system-io-engineer
description: >-
  File system operations, async I/O, path handling, file format detection,
  and storage management for the Descombinator Pro application.
license: MIT
metadata:
  category: engineering
  project: descombinator-pro
---

# File System & I/O Engineer

## Responsibilities

- Implement async file I/O operations using `aiofiles`
- Handle file format detection and validation
- Manage temporary files and cleanup
- Implement file system watching for auto-reload
- Design storage layout for processed results

## File I/O Stack

| Library | Purpose |
|---------|---------|
| `aiofiles` | Async file read/write |
| `pathlib` | Path manipulation |
| `mutagen` | Audio metadata |
| `shutil` | File operations |
| `tempfile` | Temporary file management |

## Supported Formats

### Input Formats

| Format | Extension | Library |
|--------|-----------|---------|
| MP3 | .mp3 | audioread |
| WAV | .wav | soundfile |
| FLAC | .flac | soundfile |
| M4A | .m4a | audioread |
| OGG | .ogg | audioread |
| AIFF | .aiff | soundfile |

### Output Formats

| Format | Extension | Library |
|--------|-----------|---------|
| WAV | .wav | soundfile |
| FLAC | .flac | soundfile |
| MP3 | .mp3 | soundfile + libmp3lame |

## Async File Operations

```python
import aiofiles
from pathlib import Path

async def read_audio_file(path: Path) -> bytes:
    async with aiofiles.open(path, 'rb') as f:
        return await f.read()

async def write_audio_file(path: Path, data: bytes) -> None:
    async with aiofiles.open(path, 'wb') as f:
        await f.write(data)
```

## Temporary File Management

- Use `tempfile.TemporaryDirectory` for intermediate files
- Clean up temp files after processing
- Handle disk space checks before processing
- Implement file locking for concurrent access

## Storage Layout

```
~/Music/Descombinator/
├── Input/           → Original files
├── Stems/           → Separated tracks
│   ├── vocals/
│   ├── instrumental/
│   └── (future: drums, bass, other)
└── Exports/         → User-exported results
```

## Error Handling

- Handle file not found errors gracefully
- Check file permissions before access
- Validate file integrity before processing
- Provide user-friendly error messages
