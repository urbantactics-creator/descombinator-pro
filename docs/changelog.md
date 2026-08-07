# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

#### UI Enhancements

- **Enhanced drag-and-drop visual feedback** in `FileDropZone` widget:
  - Green background with solid border when dragging supported audio files
  - Red background with solid border when dragging unsupported files
  - Smooth animated transitions between states using QPropertyAnimation
  - Dynamic text updates ("Drop to load audio file" / "Unsupported format")
  - Opacity animations for smoother visual feedback

- **Processing dialog animations**:
  - Animated progress bar with smooth easing transitions
  - Loading icon rotation animation
  - Real-time progress updates with message display
  - Smooth fade-in/fade-out effects

- **Status bar progress indicator**:
  - Color-changing background during separation (green → yellow → red)
  - Animated hourglass icon for visual feedback
  - Screen transition effects when separation starts/completes

- **MainWindow transition effects**:
  - Fade-out effect when separation starts
  - Fade-in effect when separation completes
  - Processing dialog entrance animation with bounce effect

### Changed

- **FileDropZone widget** (`app/widgets/file_drop_zone.py`):
  - Added `_setup_animations()` method for animation configuration
  - Enhanced `_apply_drag_style()` to support valid/invalid file states
  - Added opacity effects for smoother transitions
  - Improved visual feedback with background colors

- **ProcessingDialog** (`app/ui/processing_dialog.py`):
  - Added animated progress bar with looping animation
  - Added loading icon rotation animation
  - Added `update_progress()` method for real-time updates
  - Added `set_complete()`, `set_error()`, `set_cancelled()` methods

- **MainWindow** (`app/ui/main_window.py`):
  - Added `_start_transition()` method for screen transitions
  - Added `_reverse_transition()` method for completion transitions
  - Added `_show_processing_dialog()` and `_hide_processing_dialog()` methods
  - Added `_transition_active` flag to prevent overlapping transitions
  - Added progress icon to status bar

### Documentation

- Updated user guide with new UI features and animations
- Added comprehensive docstrings to FileDropZone widget
- Added docstrings to ProcessingDialog class and methods
- Updated development guide with additional workflow steps

### Tests

- Added unit tests for FileDropZone widget animations
- Added unit tests for ProcessingDialog animations
- Added UI tests for status bar progress indicator
- Added integration tests for screen transitions

## [0.1.0] - 2026-08-02

### Added

- Initial release of Descombinator Pro
- Audio separation using Demucs and Open-Unmix models
- Multi-track playback with volume and mute controls
- Waveform visualization
- Export functionality (WAV, FLAC, MP3, M4A)
- Settings dialog with model selection
- Dark/light theme support
- Progress tracking and cancellation
- Thermal monitoring
- Drag-and-drop file loading
