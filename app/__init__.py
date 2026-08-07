"""Descombinator Pro presentation layer.

This package contains the UI layer of the application, including:
- Controllers: MainController, PlaybackController, SettingsController
- Services: ExportService, PlaybackService, PlaybackStateStore, SeparationService
- Widgets: FileDropZone, PlaybackControls, ProgressBar, TrackMixerWidget,
  TrackSelector, WaveformView
- UI Layouts: MainWindow, ProcessingDialog, SettingsDialog
- Audio: AudioMixer, MixerTrack, PlaybackState
- Workers: AudioLoadWorker
- Models: AppState, ProcessingState, SettingsModel
"""

__all__ = [
    # Controllers
    "MainController",
    "PlaybackController",
    "SettingsController",
    # Services
    "ExportService",
    "PlaybackService",
    "PlaybackStateStore",
    "SeparationService",
    # Widgets
    "FileDropZone",
    "PlaybackControls",
    "ProgressBar",
    "TrackMixerWidget",
    "TrackSelector",
    "WaveformView",
    # UI
    "MainWindow",
    "ProcessingDialog",
    "SettingsDialog",
    # Audio
    "AudioMixer",
    "MixerTrack",
    "PlaybackState",
    # Workers
    "AudioLoadWorker",
    # Models
    "AppState",
    "ProcessingState",
    "SettingsModel",
]
