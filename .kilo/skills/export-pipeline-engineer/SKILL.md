---
name: export-pipeline-engineer
description: >-
  Export pipeline design, file format conversion, metadata embedding,
  batch export, and export quality optimization.
license: MIT
metadata:
  category: engineering
  project: descombinator-pro
---

# Export Pipeline Engineer

## Responsibilities

- Design and implement the export pipeline in `engine/export/`
- Handle file format conversion and encoding
- Embed metadata (tags, artwork) in exported files
- Implement batch export functionality
- Optimize export quality and file size

## Export Pipeline

```
Separation Result → Format Selection → Encoding → Metadata → File Write
```

## Supported Export Formats

| Format | Quality | File Size | Use Case |
|--------|---------|-----------|----------|
| WAV | Lossless | Large | Professional use |
| FLAC | Lossless | Medium | Archiving |
| MP3 | Lossy | Small | Sharing |
| M4A | Lossy | Small | Apple ecosystem |

## Export Configuration

```python
from pydantic import BaseModel
from enum import Enum

class ExportFormat(str, Enum):
    WAV = "wav"
    FLAC = "flac"
    MP3 = "mp3"
    M4A = "m4a"

class ExportConfig(BaseModel):
    format: ExportFormat = ExportFormat.WAV
    sample_rate: int = 44100
    bit_depth: int = 16
    bitrate: int = 320  # kbps (for lossy formats)
    embed_metadata: bool = True
    normalize: bool = True
```

## Metadata Embedding

### Tags to Embed

- Title (original filename)
- Artist (from source metadata)
- Album (Descombinator Pro)
- Track number
- Genre
- Year
- Comments ("Separated with Descombinator Pro")

### Artwork

- Embed original album art if available
- Generate placeholder artwork if not
- Support custom artwork selection

## Batch Export

- Export multiple files with same settings
- Progress tracking per file
- Error handling for individual files
- Resume capability for interrupted exports

## Quality Optimization

### WAV Export

- 16-bit or 24-bit PCM
- 44.1 kHz or 48 kHz sample rate
- No compression

### MP3 Export

- Bitrate: 192-320 kbps
- Variable bitrate (VBR) for smaller files
- Use LAME encoder via `soundfile`

### FLAC Export

- Compression level: 5 (default)
- Lossless encoding
- Metadata support
