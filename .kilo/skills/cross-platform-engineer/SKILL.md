---
name: cross-platform-engineer
description: >-
  Cross-platform compatibility, platform-specific code, packaging for
  Windows/macOS/Linux, and platform testing for the Descombinator Pro application.
license: MIT
metadata:
  category: engineering
  project: descombinator-pro
---

# Cross-Platform Engineer

## Responsibilities

- Ensure the application runs on Windows, macOS, and Linux
- Handle platform-specific code paths
- Test on all supported platforms
- Manage platform-specific dependencies
- Implement platform-appropriate UI conventions

## Supported Platforms

| Platform | Version | Architecture |
|----------|---------|-------------|
| Windows | 10, 11 | x64 |
| macOS | 12+ | ARM64, x64 |
| Linux | Ubuntu 22.04+, Fedora 38+ | x64, ARM64 |

## Platform-Specific Considerations

### Windows

- Use `PySide6` for native Windows look and feel
- Handle Windows path conventions (`\` vs `/`)
- Support Windows audio APIs (WASAPI)
- Package with PyInstaller for `.exe`

### macOS

- Support Apple Silicon (ARM64) natively
- Use `PySide6` for native macOS look and feel
- Handle macOS code signing for distribution
- Support macOS audio APIs (CoreAudio)
- Package with PyInstaller for `.app`

### Linux

- Support major distributions (Ubuntu, Fedora, Arch)
- Handle various audio subsystems (ALSA, PulseAudio, PipeWire)
- Package as AppImage, Flatpak, or DEB/RPM
- Use `PySide6` for native Linux look and feel

## Path Handling

```python
from pathlib import Path
import platform

def get_app_data_dir() -> Path:
    system = platform.system()
    if system == "Windows":
        return Path(os.environ["APPDATA"]) / "Descombinator"
    elif system == "Darwin":
        return Path.home() / "Library" / "Application Support" / "Descombinator"
    else:  # Linux
        return Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local/share")) / "descombinator"
```

## Platform Testing

### CI/CD Matrix

| Platform | Python | Tests |
|----------|--------|-------|
| Windows | 3.12 | UI, separation, export |
| macOS | 3.12 | UI, separation, export |
| Linux | 3.12 | UI, separation, export |

### Platform-Specific Tests

- File dialog behavior
- Audio device enumeration
- Keyboard shortcuts
- Window management
- File system permissions
