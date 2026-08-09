"""Settings dialog for application configuration."""

from pathlib import Path

from loguru import logger
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QGroupBox,
    QLabel,
    QMessageBox,
    QPushButton,
    QSpinBox,
    QVBoxLayout,
)

from app.controllers.settings_controller import SettingsController
from app.models.settings_model import SettingsModel
from engine.export.config import ExportFormat
from engine.inference.config import ModelName


class SettingsDialog(QDialog):
    """Dialog for editing application settings."""

    def __init__(
        self,
        settings_controller: SettingsController,
        parent: object | None = None,
    ) -> None:
        super().__init__(parent)
        self._settings_controller = settings_controller
        self._settings = SettingsModel(**settings_controller._settings.model_dump())

        self.setWindowTitle("Settings")
        self.setMinimumWidth(480)
        self.setModal(True)
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)

        self._setup_ui()
        self._load_values()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        # --- Separation group ---
        sep_group = QGroupBox("Separation")
        sep_form = QFormLayout(sep_group)

        self._model_combo = QComboBox()
        for model in ModelName:
            self._model_combo.addItem(model.value, model)
        sep_form.addRow("Model:", self._model_combo)

        self._segment_spin = QSpinBox()
        self._segment_spin.setRange(0, 300)
        self._segment_spin.setSpecialValueText("Auto (default)")
        self._segment_spin.setSuffix(" s")
        sep_form.addRow("Segment:", self._segment_spin)

        self._mixed_precision_check = QCheckBox("Mixed precision (GPU)")
        sep_form.addRow(self._mixed_precision_check)

        self._pin_memory_check = QCheckBox("Pin memory (GPU)")
        sep_form.addRow(self._pin_memory_check)

        layout.addWidget(sep_group)

        # --- Export group ---
        export_group = QGroupBox("Export")
        export_form = QFormLayout(export_group)

        self._format_combo = QComboBox()
        for fmt in ExportFormat:
            self._format_combo.addItem(fmt.value.upper(), fmt)
        export_form.addRow("Format:", self._format_combo)

        self._sample_rate_spin = QSpinBox()
        self._sample_rate_spin.setRange(8000, 192000)
        self._sample_rate_spin.setSingleStep(100)
        self._sample_rate_spin.setSuffix(" Hz")
        export_form.addRow("Sample Rate:", self._sample_rate_spin)

        self._bit_depth_combo = QComboBox()
        self._bit_depth_combo.addItems(["16", "24", "32"])
        export_form.addRow("Bit Depth:", self._bit_depth_combo)

        self._bitrate_spin = QSpinBox()
        self._bitrate_spin.setRange(32, 320)
        self._bitrate_spin.setSingleStep(32)
        self._bitrate_spin.setSuffix(" kbps")
        export_form.addRow("Bitrate:", self._bitrate_spin)

        self._normalize_check = QCheckBox("Normalize audio")
        export_form.addRow(self._normalize_check)

        self._fade_in_spin = QSpinBox()
        self._fade_in_spin.setRange(0, 10000)
        self._fade_in_spin.setSuffix(" ms")
        export_form.addRow("Fade In:", self._fade_in_spin)

        self._fade_out_spin = QSpinBox()
        self._fade_out_spin.setRange(0, 10000)
        self._fade_out_spin.setSuffix(" ms")
        export_form.addRow("Fade Out:", self._fade_out_spin)

        layout.addWidget(export_group)

        # --- Output group ---
        output_group = QGroupBox("Output")
        output_form = QFormLayout(output_group)

        output_row = QVBoxLayout()
        self._output_dir_label = QLabel()
        self._output_dir_label.setWordWrap(True)
        self._output_dir_label.setTextInteractionFlags(Qt.TextSelectableByMouse)
        output_row.addWidget(self._output_dir_label)

        browse_btn = QPushButton("Browse...")
        browse_btn.clicked.connect(self._browse_output_dir)
        output_row.addWidget(browse_btn)

        output_form.addRow("Output Directory:", output_row)

        layout.addWidget(output_group)

        # --- Appearance group ---
        appearance_group = QGroupBox("Appearance")
        appearance_form = QFormLayout(appearance_group)

        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["dark", "light"])
        appearance_form.addRow("Theme:", self._theme_combo)

        layout.addWidget(appearance_group)

        # --- Accessibility group ---
        accessibility_group = QGroupBox("Accessibility")
        accessibility_layout = QVBoxLayout(accessibility_group)

        self._reduced_motion_check = QCheckBox("Reduce motion (disable animations)")
        accessibility_layout.addWidget(self._reduced_motion_check)

        self._high_contrast_check = QCheckBox("High contrast")
        accessibility_layout.addWidget(self._high_contrast_check)

        layout.addWidget(accessibility_group)

        # --- Buttons ---
        self._button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel
        )
        self._button_box.accepted.connect(self._on_save)
        self._button_box.rejected.connect(self.reject)
        layout.addWidget(self._button_box)

    def _load_values(self) -> None:
        """Load current settings into the form controls."""
        s = self._settings

        idx = self._model_combo.findData(s.default_model)
        if idx >= 0:
            self._model_combo.setCurrentIndex(idx)

        self._segment_spin.setValue(s.segment or 0)
        self._mixed_precision_check.setChecked(s.mixed_precision)
        self._pin_memory_check.setChecked(s.pin_memory)

        fmt_idx = self._format_combo.findData(s.default_format)
        if fmt_idx >= 0:
            self._format_combo.setCurrentIndex(fmt_idx)

        self._sample_rate_spin.setValue(s.sample_rate)
        self._bit_depth_combo.setCurrentText(str(s.bit_depth))
        self._bitrate_spin.setValue(s.bitrate // 1000)
        self._normalize_check.setChecked(s.normalize)
        self._fade_in_spin.setValue(int(s.fade_in * 1000))
        self._fade_out_spin.setValue(int(s.fade_out * 1000))

        self._output_dir_label.setText(str(s.output_dir))

        theme_idx = self._theme_combo.findText(s.theme)
        if theme_idx >= 0:
            self._theme_combo.setCurrentIndex(theme_idx)

        self._reduced_motion_check.setChecked(getattr(s, "reduced_motion", False))
        self._high_contrast_check.setChecked(getattr(s, "high_contrast", False))

    def _browse_output_dir(self) -> None:
        """Open a directory chooser for the output directory."""
        current = self._output_dir_label.text()
        directory = QFileDialog.getExistingDirectory(
            self, "Select Output Directory", current
        )
        if directory:
            self._output_dir_label.setText(directory)

    def _on_save(self) -> None:
        """Save settings and close dialog."""
        try:
            self._settings.default_model = self._model_combo.currentData()
            self._settings.default_format = self._format_combo.currentData()
            self._settings.output_dir = Path(self._output_dir_label.text())
            self._settings.theme = self._theme_combo.currentText()
            segment = self._segment_spin.value()
            self._settings.segment = segment if segment > 0 else None
            self._settings.mixed_precision = self._mixed_precision_check.isChecked()
            self._settings.pin_memory = self._pin_memory_check.isChecked()
            self._settings.reduced_motion = self._reduced_motion_check.isChecked()
            self._settings.high_contrast = self._high_contrast_check.isChecked()
            self._settings.sample_rate = self._sample_rate_spin.value()
            self._settings.bit_depth = int(self._bit_depth_combo.currentText())
            self._settings.bitrate = self._bitrate_spin.value() * 1000
            self._settings.normalize = self._normalize_check.isChecked()
            self._settings.fade_in = self._fade_in_spin.value() / 1000.0
            self._settings.fade_out = self._fade_out_spin.value() / 1000.0

            self._settings_controller.save_settings(self._settings)
            self._settings_controller._settings = self._settings.model_copy()
            self._settings_controller.settings_changed.emit(self._settings)
            self.accept()
        except Exception as e:
            logger.error(f"Failed to save settings: {e}")
            QMessageBox.warning(self, "Settings Error", f"Failed to save: {e}")
