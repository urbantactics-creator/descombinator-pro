---
name: configuration-manager
description: >-
  Application configuration management, environment variables, settings
  validation, config file handling, and configuration best practices.
license: MIT
metadata:
  category: engineering
  project: descombinator-pro
---

# Configuration Manager

## Responsibilities

- Design and implement configuration management
- Handle environment variables and config files
- Validate configuration at startup
- Provide configuration documentation
- Manage configuration for different environments

## Configuration Sources

| Source | Priority | Purpose |
|--------|----------|---------|
| Environment variables | Highest | Secrets, deployment config |
| Config file | Medium | User preferences |
| Defaults | Lowest | Fallback values |

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `LOG_FILE` | None | Log file path (None = console only) |
| `MODEL_CACHE_DIR` | `~/.cache/descombinator` | Model weights cache directory |
| `MAX_WORKERS` | CPU count | Maximum parallel processing workers |
| `TEMP_DIR` | System temp | Temporary file directory |
| `DEFAULT_SAMPLE_RATE` | `44100` | Default audio sample rate |
| `DEFAULT_OUTPUT_FORMAT` | `wav` | Default export format |

## Configuration Model

```python
from pydantic import BaseSettings, Field

class Settings(BaseSettings):
    log_level: str = "INFO"
    log_file: str | None = None
    model_cache_dir: Path = Field(default_factory=lambda: Path.home() / ".cache" / "descombinator")
    max_workers: int = Field(default_factory=os.cpu_count)
    temp_dir: Path = Field(default_factory=Path.tempdir)
    default_sample_rate: int = 44100
    default_output_format: str = "wav"

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
```

## Config File

### Location

- Linux: `~/.config/descombinator/config.yaml`
- macOS: `~/Library/Preferences/descombinator/config.yaml`
- Windows: `%APPDATA%\Descombinator\config.yaml`

### Format

```yaml
# User preferences
ui:
  theme: dark
  language: en
  show_waveform: true

processing:
  model: htdemucs_ft
  sample_rate: 44100
  batch_size: 1

export:
  format: wav
  bit_depth: 16
  normalize: true
```

## Validation

- Validate configuration at application startup
- Provide clear error messages for invalid config
- Use sensible defaults for missing values
- Support config file migration between versions
