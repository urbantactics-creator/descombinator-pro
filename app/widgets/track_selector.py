"""Track selector widget for choosing separation stems."""

from __future__ import annotations

from PySide6.QtCore import Signal
from PySide6.QtWidgets import (
    QButtonGroup,
    QCheckBox,
    QGroupBox,
    QHBoxLayout,
    QVBoxLayout,
    QWidget,
)


class TrackSelector(QWidget):
    """Widget for selecting which stems to separate."""

    stems_changed = Signal(list)

    DEFAULT_STEMS = ["vocals", "drums", "bass", "other"]

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        layout = QVBoxLayout(self)

        self._group_box = QGroupBox("Select stems to separate")
        layout.addWidget(self._group_box)

        group_layout = QHBoxLayout()
        self._group_box.setLayout(group_layout)

        self._button_group = QButtonGroup()
        self._button_group.setExclusive(False)

        self._checkboxes: dict[str, QCheckBox] = {}
        for stem in self.DEFAULT_STEMS:
            checkbox = QCheckBox(stem.capitalize())
            checkbox.setChecked(stem in ["vocals", "other"])  # Default selection
            checkbox.stateChanged.connect(self._on_state_changed)
            self._button_group.addButton(checkbox)
            self._checkboxes[stem] = checkbox
            group_layout.addWidget(checkbox)

        layout.addStretch()

    def _on_state_changed(self) -> None:
        """Emit stems_changed with the currently selected stems."""
        selected_stems = [
            stem for stem, checkbox in self._checkboxes.items() if checkbox.isChecked()
        ]
        self.stems_changed.emit(selected_stems)

    @property
    def selected_stems(self) -> list[str]:
        """Currently selected stem names."""
        return [
            stem for stem, checkbox in self._checkboxes.items() if checkbox.isChecked()
        ]

    def set_selected_stems(self, stems: list[str]) -> None:
        """Sync checkbox state with an external stem list and emit stems_changed."""
        for stem, checkbox in self._checkboxes.items():
            checkbox.setChecked(stem in stems)

    def clear_selection(self) -> None:
        """Uncheck all stem checkboxes."""
        for checkbox in self._checkboxes.values():
            checkbox.setChecked(False)
