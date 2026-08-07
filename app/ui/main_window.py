"""Main window for the Descombinator Pro application."""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
from loguru import logger
from PySide6.QtCore import Qt, QThreadPool, Slot
from PySide6.QtGui import QAction, QCloseEvent, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController
from app.models.settings_model import SettingsModel
from app.ui.processing_dialog import ProcessingDialog
from app.ui.settings_dialog import SettingsDialog
from app.widgets.file_drop_zone import FileDropZone
from app.widgets.playback_controls import PlaybackControls
from app.widgets.progress_bar import ProgressBar
from app.widgets.track_mixer import TrackMixerWidget
from app.widgets.track_selector import TrackSelector
from app.widgets.waveform_view import WaveformView
from app.workers.audio_load_worker import AudioLoadWorker


def _styles_path(theme: str) -> Path:
    """Resolve the stylesheet path for dev and PyInstaller builds (regression A8).

    Frozen builds bundle ``app/resources`` under ``sys._MEIPASS``; in dev the
    app package lives at ``<project_root>/app``.
    """
    if getattr(sys, "frozen", False):
        base = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    else:
        base = Path(__file__).resolve().parent.parent  # <root>/app
    return base / "resources" / "styles" / f"{theme}.qss"


class MainWindow(QMainWindow):
    """Main application window."""

    def __init__(
        self,
        main_controller: MainController,
        playback_controller: PlaybackController,
        settings_controller: SettingsController,
    ) -> None:
        super().__init__()
        self._main_controller = main_controller
        self._playback_controller = playback_controller
        self._settings_controller = settings_controller
        self._separated_stems: dict[str, np.ndarray] = {}
        self._processing_dialog: ProcessingDialog | None = None
        self._export_dialog: ProcessingDialog | None = None
        self._export_worker: object | None = None
        self._thread_pool = QThreadPool.globalInstance()

        self.setWindowTitle("Descombinator Pro")
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._connect_signals()
        self._load_stylesheet()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        main_layout = QVBoxLayout(central_widget)

        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        self._file_drop_zone = FileDropZone()
        left_layout.addWidget(self._file_drop_zone)

        self._track_selector = TrackSelector()
        left_layout.addWidget(self._track_selector)

        self._progress_bar = ProgressBar()
        left_layout.addWidget(self._progress_bar)

        self._separate_btn = QPushButton("Separate")
        self._separate_btn.setObjectName("primaryButton")
        self._separate_btn.setEnabled(False)
        self._separate_btn.clicked.connect(self._on_separate_clicked)
        left_layout.addWidget(self._separate_btn)

        left_layout.addStretch()

        splitter.addWidget(left_panel)

        # Right panel - visualization and playback
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        self._waveform_view = WaveformView()
        right_layout.addWidget(self._waveform_view, stretch=2)

        self._playback_controls = PlaybackControls()
        right_layout.addWidget(self._playback_controls)

        self._track_mixer = TrackMixerWidget()
        right_layout.addWidget(self._track_mixer)

        splitter.addWidget(right_panel)

        splitter.setSizes([300, 450])

        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_label = QLabel("Ready")
        self._status_label.setObjectName("statusLabel")
        self._status_bar.addWidget(self._status_label)
        self._file_info_label = QLabel("")
        self._status_bar.addPermanentWidget(self._file_info_label)

        # Progress icon for separation animations
        self._progress_icon = QLabel("⏳")
        self._progress_icon.setObjectName("progressIcon")
        self._progress_icon.setStyleSheet("color: #666; font-size: 12px;")
        self._progress_icon.hide()
        self._status_bar.addPermanentWidget(self._progress_icon)

        self._create_menu_bar()

    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("&File")

        open_action = QAction("Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        self._export_action = QAction("Export...", self)
        self._export_action.setShortcut("Ctrl+E")
        self._export_action.triggered.connect(self._export_audio)
        self._export_action.setEnabled(False)
        file_menu.addAction(self._export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("&View")

        theme_menu = view_menu.addMenu("Theme")

        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self._change_theme("light"))
        theme_menu.addAction(light_action)

        dark_action = QAction("Dark", self)
        dark_action.setChecked(True)
        dark_action.triggered.connect(lambda: self._change_theme("dark"))
        theme_menu.addAction(dark_action)

        settings_action = QAction("Settings...", self)
        settings_action.setShortcut("Ctrl+,")
        settings_action.triggered.connect(self._open_settings)
        view_menu.addAction(settings_action)

        # Help menu
        help_menu = menubar.addMenu("&Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _connect_signals(self) -> None:
        """Connect signals from widgets and controllers."""
        self._file_drop_zone.file_dropped.connect(self._on_file_dropped)
        self._track_selector.stems_changed.connect(self._on_stems_changed)
        # Sync initial stem selection with controller state
        self._on_stems_changed(self._track_selector.selected_stems)

        self._playback_controls.play_clicked.connect(self._playback_controller.play)
        self._playback_controls.pause_clicked.connect(self._playback_controller.pause)
        self._playback_controls.stop_clicked.connect(self._playback_controller.stop)
        self._playback_controls.position_changed.connect(
            self._playback_controller.set_position
        )
        self._playback_controls.volume_changed.connect(
            self._playback_controller.set_volume
        )

        self._main_controller.state_changed.connect(self._on_state_changed)
        self._main_controller.separation_started.connect(self._on_separation_started)
        self._main_controller.separation_completed.connect(
            self._on_separation_completed
        )
        self._main_controller.separation_failed.connect(self._on_separation_failed)
        self._main_controller.separation_progress.connect(self._on_separation_progress)
        self._main_controller.thermal_warning.connect(self._on_thermal_warning)
        self._settings_controller.settings_changed.connect(self._on_settings_changed)
        self._main_controller.export_progress.connect(self._on_export_progress)
        self._main_controller.export_completed.connect(self._on_export_completed)
        self._main_controller.export_failed.connect(self._on_export_failed)

        self._playback_controller.position_changed.connect(
            self._on_playback_position_changed
        )
        self._playback_controller.duration_changed.connect(
            self._on_playback_duration_changed
        )
        self._playback_controller.state_changed.connect(self._on_playback_state_changed)
        self._playback_controller.master_volume_changed.connect(
            self._on_playback_volume_changed
        )
        self._playback_controller.error_occurred.connect(self._on_playback_error)

        self._playback_controller.tracks_changed.connect(self._on_tracks_changed)
        self._playback_controller.track_volume_changed.connect(
            self._track_mixer.set_track_volume
        )
        self._playback_controller.track_muted_changed.connect(
            self._track_mixer.set_track_muted
        )

        self._track_mixer.volume_changed.connect(self._on_track_volume_changed)
        self._track_mixer.muted_changed.connect(self._on_track_muted_changed)

    def _load_stylesheet(self) -> None:
        """Load the persisted theme's stylesheet (regression A8)."""
        self._change_theme(self._settings_controller.settings.theme)
        self._apply_accessibility()

    def _change_theme(self, theme: str) -> None:
        """Change the application theme."""
        try:
            style_path = _styles_path(theme)
            sheet = style_path.read_text(encoding="utf-8")
            if getattr(self._settings_controller.settings, "high_contrast", False):
                hc_path = style_path.parent / "high_contrast.qss"
                if hc_path.exists():
                    sheet += "\n" + hc_path.read_text(encoding="utf-8")
            self.setStyleSheet(sheet)
            logger.info(f"Applied {theme} theme")
            # Update waveform theme
            self._waveform_view.set_theme(theme)
        except FileNotFoundError:
            logger.warning(f"Stylesheet not found for theme: {theme}")
            self.setStyleSheet("")

    def _on_settings_changed(self, settings: SettingsModel) -> None:
        """Re-apply the theme when settings change."""
        self._change_theme(settings.theme)
        self._apply_accessibility()

    def _apply_accessibility(self) -> None:
        reduced = getattr(self._settings_controller.settings, "reduced_motion", False)
        for attr in ("_file_drop_zone", "_processing_dialog", "_export_dialog"):
            widget = getattr(self, attr, None)
            if widget is not None and hasattr(widget, "set_reduced_motion"):
                widget.set_reduced_motion(reduced)
        if getattr(self._settings_controller.settings, "high_contrast", False):
            self._change_theme(self._settings_controller.settings.theme)

    # --- Menu actions ---

    @Slot()
    def _open_file(self) -> None:
        """Open a file dialog to select an audio file."""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Audio Files (*.wav *.mp3 *.flac *.m4a *.ogg *.aiff)")
        file_dialog.setViewMode(QFileDialog.Detail)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self._on_file_dropped(selected_files[0])

    @Slot()
    def _open_settings(self) -> None:
        """Open the settings dialog."""
        dialog = SettingsDialog(self._settings_controller, self)
        dialog.exec()

    @Slot()
    def _export_audio(self) -> None:
        """Export the separated audio stems."""
        if not self._separated_stems:
            QMessageBox.warning(self, "Export Error", "No audio to export")
            return

        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.Directory)

        if file_dialog.exec():
            selected_dir = file_dialog.selectedFiles()[0]
            Path(selected_dir)

            # Show progress dialog
            self._export_dialog = ProcessingDialog(self)
            self._export_dialog.setWindowTitle("Exporting Audio")
            self._export_dialog.cancel_requested.connect(self._on_export_cancelled)
            self._export_dialog.show()

            # Create and start export worker
            def export_progress_callback(percent: int, message: str) -> None:
                self._export_dialog.update_progress(percent, message)

            self._export_worker = self._main_controller._export_worker
            self._export_worker.signals.progress.connect(export_progress_callback)
            self._export_worker.signals.finished.connect(self._on_export_finished)
            self._export_worker.signals.error.connect(self._on_export_error)

            self._thread_pool.start(self._export_worker)

    @Slot()
    def _on_export_cancelled(self) -> None:
        """Handle export cancellation."""
        if self._export_worker:
            self._export_worker.cancel()
            self._export_dialog.set_cancelled()

    @Slot(dict)
    def _on_export_finished(self, result: dict[str, Path]) -> None:
        """Handle successful export completion."""
        stem_names = ", ".join(result.keys())
        QMessageBox.information(
            self,
            "Export Complete",
            f"Successfully exported {len(result)} stem(s):\n\n{stem_names}",
        )
        if self._export_dialog:
            self._export_dialog.set_complete()
            self._export_dialog = None

    @Slot(str)
    def _on_export_error(self, error_message: str) -> None:
        """Handle export error."""
        QMessageBox.critical(self, "Export Error", error_message)
        if self._export_dialog:
            self._export_dialog.set_error(error_message)
            self._export_dialog = None

    @Slot()
    def _show_about(self) -> None:
        """Show the about dialog."""
        QMessageBox.about(
            self,
            "About Descombinator Pro",
            """
            <h2>Descombinator Pro</h2>
            <p>Audio source separation application using AI models.</p>
            <p>Version 0.1.0</p>
            <p>&copy; 2026 Descombinator Team</p>
            """,
        )

    # --- File drop / load ---

    @Slot(str)
    def _on_file_dropped(self, file_path: str) -> None:
        """Handle a file being dropped on the drop zone."""
        self._playback_controller.reset()
        self._playback_controller.record_last_file(file_path)
        self._main_controller.handle_file_dropped(file_path)
        self._status_label.setText(f"Loaded: {Path(file_path).name}")
        self._separate_btn.setEnabled(True)

        # Load audio in background thread for waveform display
        worker = AudioLoadWorker(Path(file_path))
        worker.signals.finished.connect(self._on_audio_loaded)
        worker.signals.display_ready.connect(self._on_display_ready)
        worker.signals.error.connect(self._on_audio_load_error)
        QThreadPool.globalInstance().start(worker)

    @Slot(object)
    def _on_audio_loaded(self, result: object) -> None:
        """Handle audio loaded successfully for waveform and playback."""
        audio_data: np.ndarray
        sample_rate: int
        audio_data, sample_rate = result  # type: ignore[misc]
        self._main_controller.set_loaded_audio(audio_data, sample_rate)
        self._waveform_view.set_audio_data(audio_data, sample_rate)
        self._playback_controller.set_source(audio_data, sample_rate)

    @Slot(object)
    def _on_display_ready(self, result: object) -> None:
        """Render the worker-decimated waveform points."""
        points: np.ndarray
        time_step: float
        total_time: float
        points, time_step, total_time = result  # type: ignore[misc]
        self._waveform_view.set_display_data(points, time_step, total_time)

    @Slot(str)
    def _on_audio_load_error(self, error: str) -> None:
        """Handle audio load failure."""
        self._status_label.setText(f"Error loading audio: {error}")

    # --- Stem selection ---

    @Slot(list)
    def _on_stems_changed(self, stems: list[str]) -> None:
        """Handle the user changing which stems to process."""
        self._main_controller.handle_stems_changed(stems)

    # --- Separate ---

    @Slot()
    def _on_separate_clicked(self) -> None:
        """Handle the separate button click."""
        self._main_controller.handle_separate_requested()

    # --- Controller state ---

    @Slot(object)
    def _on_state_changed(self, app_state: object) -> None:
        """Handle application state changes."""
        from app.models.processing_state import ProcessingState

        if hasattr(app_state, "processing_status"):
            status = app_state.processing_status
            is_processing = status in (
                ProcessingState.LOADING,
                ProcessingState.PROCESSING,
            )
            self._separate_btn.setEnabled(
                not is_processing
                and self._main_controller._app_state.current_file is not None
            )
            self._file_drop_zone.setEnabled(not is_processing)
            self._track_selector.setEnabled(not is_processing)
            if is_processing:
                self._status_label.setText(f"Processing: {status.value}")
            elif status == ProcessingState.COMPLETE:
                self._status_label.setText("Ready")
            elif status == ProcessingState.ERROR:
                self._status_label.setText("Error")
            elif status == ProcessingState.CANCELLED:
                self._status_label.setText("Cancelled")

    # --- Separation signals ---

    @Slot()
    def _on_separation_started(self) -> None:
        """Handle separation process starting."""
        self._status_label.setText("Starting separation...")
        self._progress_bar.show()
        self._progress_bar.set_progress(0, "Initializing...")

        self._processing_dialog = ProcessingDialog(self)
        self._processing_dialog.show()

    @Slot(dict)
    def _on_separation_completed(self, stems: dict[str, np.ndarray]) -> None:
        """Handle separation process completion."""
        self._separated_stems = stems
        self._status_label.setText("Separation complete!")
        self._progress_bar.set_progress(100, "Complete")
        self._export_action.setEnabled(True)

        if self._processing_dialog:
            self._processing_dialog.set_complete()
            self._processing_dialog = None

        # Feed stems into playback and rebuild the track mixer
        self._playback_controller.set_stems(stems)

        # Update waveform with first stem (vocals preferred)
        # Use the sample rate from the loaded audio (stored in controller)
        sample_rate = self._main_controller._loaded_sample_rate
        if "vocals" in stems:
            self._waveform_view.set_audio_data(stems["vocals"], sample_rate)
        elif stems:
            first_stem = next(iter(stems.values()))
            self._waveform_view.set_audio_data(first_stem, sample_rate)

    @Slot(str)
    def _on_separation_failed(self, error_message: str) -> None:
        """Handle separation process failure."""
        self._status_label.setText(f"Error: {error_message}")
        self._progress_bar.set_error(error_message)

        if self._processing_dialog:
            self._processing_dialog.set_error(error_message)
            self._processing_dialog = None

    @Slot(int, str)
    def _on_separation_progress(self, percent: int, message: str) -> None:
        """Handle separation progress updates."""
        self._status_label.setText(message)
        self._progress_bar.set_progress(percent, message)

        if self._processing_dialog:
            self._processing_dialog.update_progress(percent, message)

    @Slot(int, str)
    def _on_export_progress(self, percent: int, message: str) -> None:
        """Handle export progress updates."""
        self._status_label.setText(message)
        if self._export_dialog:
            self._export_dialog.update_progress(percent, message)

    @Slot(dict)
    def _on_export_completed(self, result: dict[str, Path]) -> None:
        """Handle successful export completion."""
        stem_names = ", ".join(result.keys())
        QMessageBox.information(
            self,
            "Export Complete",
            f"Successfully exported {len(result)} stem(s):\n\n{stem_names}",
        )
        if self._export_dialog:
            self._export_dialog.set_complete()
            self._export_dialog = None

    @Slot(str)
    def _on_export_failed(self, error_message: str) -> None:
        """Handle export error."""
        QMessageBox.critical(self, "Export Error", error_message)
        if self._export_dialog:
            self._export_dialog.set_error(error_message)
            self._export_dialog = None

    @Slot(str, float)
    def _on_thermal_warning(self, state: str, cpu_temp: float) -> None:
        """Display thermal status in the status bar."""
        if cpu_temp is not None:
            self._status_bar.showMessage(f"Thermal: {state} ({cpu_temp:.0f}°C)", 5000)

    # --- Playback signals ---

    @Slot(int)
    def _on_playback_position_changed(self, position_ms: int) -> None:
        """Handle playback position changes."""
        self._playback_controls.set_position(position_ms)
        self._waveform_view.set_position(position_ms / 1000)

    @Slot(int)
    def _on_playback_duration_changed(self, duration_ms: int) -> None:
        """Handle playback duration changes."""
        self._playback_controls.set_duration(duration_ms)

    @Slot(str)
    def _on_playback_state_changed(self, state: str) -> None:
        """Handle playback state changes."""
        self._playback_controls.set_playing(state == "playing")

    @Slot(float)
    def _on_playback_volume_changed(self, volume: float) -> None:
        """Handle playback volume changes."""
        self._playback_controls.set_volume(volume)

    @Slot(str)
    def _on_playback_error(self, error_message: str) -> None:
        """Handle playback errors."""
        self._status_label.setText(f"Playback error: {error_message}")
        QMessageBox.warning(self, "Playback Error", error_message)

    # --- Track mixer signals ---

    @Slot(list)
    def _on_tracks_changed(self, stems: list[str]) -> None:
        """Rebuild the track mixer when the loaded stems change."""
        self._track_mixer.set_tracks(
            stems,
            self._playback_controller.track_volumes(),
            self._playback_controller.muted_map(),
        )

    @Slot(str, float)
    def _on_track_volume_changed(self, name: str, volume: float) -> None:
        """Forward a mixer volume change to the playback controller."""
        self._playback_controller.set_track_volume(name, volume)

    @Slot(str, bool)
    def _on_track_muted_changed(self, name: str, muted: bool) -> None:
        """Forward a mixer mute change to the playback controller."""
        self._playback_controller.set_track_muted(name, muted)

    # --- Drag and drop ---

    def dragEnterEvent(self, event: QDragEnterEvent) -> None:
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent) -> None:
        """Handle drop events."""
        if event.mimeData().hasUrls():
            url = event.mimeData().urls()[0]
            file_path = url.toLocalFile()
            self._on_file_dropped(file_path)
            event.acceptProposedAction()

    def closeEvent(self, event: QCloseEvent) -> None:
        """Safely shut down workers and controllers before closing."""
        logger.info("Application closing, shutting down...")

        # Cancel any running separation
        if self._main_controller._current_worker is not None:
            self._main_controller.cancel_separation()

        # Stop playback
        self._playback_controller.stop()

        # Close processing dialog if open
        if self._processing_dialog is not None:
            self._processing_dialog.close()
            self._processing_dialog = None

        # Close export dialog if open
        if self._export_dialog is not None:
            self._export_dialog.close()
            self._export_dialog = None

        # Wait for thread pool to finish (max 3 seconds)
        pool = QThreadPool.globalInstance()
        if pool is not None:
            pool.waitForDone(3000)

        event.accept()
