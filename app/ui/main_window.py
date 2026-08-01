"""Main window for the Descombinator Pro application."""

from __future__ import annotations

from pathlib import Path

from loguru import logger
from PySide6.QtCore import Qt, Slot
from PySide6.QtGui import QAction, QDragEnterEvent, QDropEvent
from PySide6.QtWidgets import (
    QFileDialog,
    QLabel,
    QMainWindow,
    QMessageBox,
    QSplitter,
    QStatusBar,
    QVBoxLayout,
    QWidget,
)

from app.controllers.main_controller import MainController
from app.controllers.playback_controller import PlaybackController
from app.controllers.settings_controller import SettingsController
from app.widgets.file_drop_zone import FileDropZone
from app.widgets.playback_controls import PlaybackControls
from app.widgets.progress_bar import ProgressBar
from app.widgets.track_selector import TrackSelector
from app.widgets.waveform_view import WaveformView


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
        self._separated_stems: dict[str, any] = {}  # Store separation results

        self.setWindowTitle("Descombinator Pro")
        self.setMinimumSize(800, 600)

        self._setup_ui()
        self._connect_signals()
        self._load_stylesheet()

        # Initialize services
        self._main_controller.initialize_services()

    def _setup_ui(self) -> None:
        """Set up the user interface."""
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        # Main layout
        main_layout = QVBoxLayout(central_widget)

        # Create splitter for resizable panels
        splitter = QSplitter(Qt.Horizontal)
        main_layout.addWidget(splitter)

        # Left panel - controls
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)

        # File drop zone
        self._file_drop_zone = FileDropZone()
        left_layout.addWidget(self._file_drop_zone)

        # Track selector
        self._track_selector = TrackSelector()
        left_layout.addWidget(self._track_selector)

        # Progress bar
        self._progress_bar = ProgressBar()
        left_layout.addWidget(self._progress_bar)

        # Add stretch to push controls to top
        left_layout.addStretch()

        splitter.addWidget(left_panel)

        # Right panel - visualization and playback
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)

        # Waveform view
        self._waveform_view = WaveformView()
        right_layout.addWidget(self._waveform_view, stretch=2)

        # Playback controls
        self._playback_controls = PlaybackControls()
        right_layout.addWidget(self._playback_controls)

        splitter.addWidget(right_panel)

        # Set splitter sizes (40% left, 60% right)
        splitter.setSizes([300, 450])

        # Status bar
        self._status_bar = QStatusBar()
        self.setStatusBar(self._status_bar)
        self._status_label = QLabel("Ready")
        self._status_bar.addWidget(self._status_label)

        # Menu bar
        self._create_menu_bar()

    def _create_menu_bar(self) -> None:
        """Create the application menu bar."""
        menubar = self.menuBar()

        # File menu
        file_menu = menubar.addMenu("File")

        open_action = QAction("Open...", self)
        open_action.setShortcut("Ctrl+O")
        open_action.triggered.connect(self._open_file)
        file_menu.addAction(open_action)

        file_menu.addSeparator()

        export_action = QAction("Export...", self)
        export_action.setShortcut("Ctrl+E")
        export_action.triggered.connect(self._export_audio)
        export_action.setEnabled(False)  # Disabled until we have results
        self._export_action = export_action
        file_menu.addAction(export_action)

        file_menu.addSeparator()

        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)

        # View menu
        view_menu = menubar.addMenu("View")

        # Theme submenu
        theme_menu = view_menu.addMenu("Theme")

        light_action = QAction("Light", self)
        light_action.triggered.connect(lambda: self._change_theme("light"))
        theme_menu.addAction(light_action)

        dark_action = QAction("Dark", self)
        dark_action.setChecked(True)  # Default
        dark_action.triggered.connect(lambda: self._change_theme("dark"))
        theme_menu.addAction(dark_action)

        # Help menu
        help_menu = menubar.addMenu("Help")

        about_action = QAction("About", self)
        about_action.triggered.connect(self._show_about)
        help_menu.addAction(about_action)

    def _connect_signals(self) -> None:
        """Connect signals from widgets and controllers."""
        # File drop zone
        self._file_drop_zone.file_dropped.connect(self._on_file_dropped)

        # Track selector
        self._track_selector.stems_changed.connect(self._on_stems_changed)

        # Playback controls
        self._playback_controls.play_clicked.connect(self._playback_controller.play)
        self._playback_controls.pause_clicked.connect(self._playback_controller.pause)
        self._playback_controls.stop_clicked.connect(self._playback_controller.stop)
        self._playback_controls.position_changed.connect(
            self._playback_controller.set_position
        )
        self._playback_controls.volume_changed.connect(
            self._playback_controller.set_volume
        )

        # Main controller
        self._main_controller.state_changed.connect(self._on_state_changed)
        self._main_controller.separation_started.connect(self._on_separation_started)
        self._main_controller.separation_completed.connect(
            self._on_separation_completed
        )
        self._main_controller.separation_failed.connect(self._on_separation_failed)
        self._main_controller.separation_progress.connect(self._on_separation_progress)

        # Playback controller
        self._playback_controller.position_changed.connect(
            self._on_playback_position_changed
        )
        self._playback_controller.duration_changed.connect(
            self._on_playback_duration_changed
        )
        self._playback_controller.state_changed.connect(self._on_playback_state_changed)
        self._playback_controller.volume_changed.connect(
            self._on_playback_volume_changed
        )
        self._playback_controller.error_occurred.connect(self._on_playback_error)

    def _load_stylesheet(self) -> None:
        """Load the application stylesheet."""
        # Default to dark theme
        self._change_theme("dark")

    def _change_theme(self, theme: str) -> None:
        """Change the application theme.

        Args:
            theme: Either "light" or "dark"
        """
        try:
            style_path = (
                f"/home/mint/Desktop/descombinator/app/resources/styles/{theme}.qss"
            )
            with open(style_path) as f:
                stylesheet = f.read()
            self.setStyleSheet(stylesheet)
            logger.info(f"Applied {theme} theme")
        except FileNotFoundError:
            logger.warning(f"Stylesheet not found: {style_path}")
            # Fallback to default style
            self.setStyleSheet("")

    @Slot()
    def _open_file(self) -> None:
        """Open a file dialog to select an audio file."""
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("Audio Files (*.wav *.mp3 *.flac *.m4a *.ogg *.aiff)")
        file_dialog.setViewMode(QFileDialog.Detail)

        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                file_path = selected_files[0]
                self._on_file_dropped(file_path)

    @Slot()
    def _export_audio(self) -> None:
        """Export the separated audio stems."""
        if not self._separated_stems:
            QMessageBox.warning(self, "Export Error", "No audio to export")
            return

        file_dialog = QFileDialog()
        file_dialog.setAcceptMode(QFileDialog.AcceptSave)
        file_dialog.setFileMode(QFileDialog.Directory)

        if file_dialog.exec():
            selected_dir = file_dialog.selectedFiles()[0]
            output_dir = Path(selected_dir)

            # TODO: Implement actual export using ExportService
            # For now, just show a message
            QMessageBox.information(
                self,
                "Export",
                f"Exporting {len(self._separated_stems)} stems to {output_dir}",
            )
            # In a real implementation, we would call the export service here

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

    # Slot implementations for handling signals

    @Slot(str)
    def _on_file_dropped(self, file_path: str) -> None:
        """Handle a file being dropped on the drop zone.

        Args:
            file_path: Path to the dropped file
        """
        self._main_controller.handle_file_dropped(file_path)
        self._status_label.setText(f"Loaded: {Path(file_path).name}")

        # Load the file into the waveform view and playback
        self._waveform_view.set_audio_data_from_file(file_path)
        self._playback_controller.load_file(file_path)

    @Slot(list)
    def _on_stems_changed(self, stems: list[str]) -> None:
        """Handle the user changing which stems to process.

        Args:
            stems: List of stem names to process
        """
        self._main_controller.handle_stems_changed(stems)

    @Slot(object)
    def _on_state_changed(self, app_state: object) -> None:
        """Handle application state changes.

        Args:
            app_state: The new application state
        """
        # Update UI based on state
        pass  # Implementation would update UI elements based on state

    @Slot()
    def _on_separation_started(self) -> None:
        """Handle separation process starting."""
        self._status_label.setText("Starting separation...")
        self._progress_bar.show()
        self._progress_bar.set_progress(0, "Initializing...")

    @Slot(dict)
    def _on_separation_completed(self, stems: dict[str, any]) -> None:
        """Handle separation process completion.

        Args:
            stems: Dictionary of separated stems
        """
        self._separated_stems = stems
        self._status_label.setText("Separation complete!")
        self._progress_bar.set_progress(100, "Complete")

        # Enable export action
        self._export_action.setEnabled(True)

        # Update waveform view with the first stem (usually vocals)
        if "vocals" in stems:
            self._waveform_view.set_audio_data(stems["vocals"])
        elif stems:
            # Use the first available stem
            first_stem = next(iter(stems.values()))
            self._waveform_view.set_audio_data(first_stem)

        # Enable playback
        # In a real implementation, we would mix the selected stems for playback

    @Slot(str)
    def _on_separation_failed(self, error_message: str) -> None:
        """Handle separation process failure.

        Args:
            error_message: Error message from the separation process
        """
        self._status_label.setText(f"Error: {error_message}")
        self._progress_bar.set_error(error_message)
        QMessageBox.critical(self, "Separation Error", error_message)

    @Slot(int, str)
    def _on_separation_progress(self, percent: int, message: str) -> None:
        """Handle separation progress updates.

        Args:
            percent: Completion percentage (0-100)
            message: Status message
        """
        self._status_label.setText(message)
        self._progress_bar.set_progress(percent, message)

    @Slot(int)
    def _on_playback_position_changed(self, position_ms: int) -> None:
        """Handle playback position changes.

        Args:
            position_ms: New position in milliseconds
        """
        # Update the playback controls position slider
        self._playback_controls.set_position(position_ms)

    @Slot(int)
    def _on_playback_duration_changed(self, duration_ms: int) -> None:
        """Handle playback duration changes.

        Args:
            duration_ms: Duration in milliseconds
        """
        # Update the playback controls duration label
        self._playback_controls.set_duration(duration_ms)

    @Slot(str)
    def _on_playback_state_changed(self, state: str) -> None:
        """Handle playback state changes.

        Args:
            state: New playback state
        """
        # Update play/pause button states
        is_playing = state == "playing"
        self._playback_controls.set_playing(is_playing)

    @Slot(float)
    def _on_playback_volume_changed(self, volume: float) -> None:
        """Handle playback volume changes.

        Args:
            volume: New volume level (0.0-1.0)
        """
        # Update the volume slider and label
        self._playback_controls.set_volume(volume)

    @Slot(str)
    def _on_playback_error(self, error_message: str) -> None:
        """Handle playback errors.

        Args:
            error_message: Error message from playback
        """
        self._status_label.setText(f"Playback error: {error_message}")
        QMessageBox.warning(self, "Playback Error", error_message)

    # Drag and drop support for the main window
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
