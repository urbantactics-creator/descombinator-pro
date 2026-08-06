"""Track mixer widget for per-track volume and mute control."""

from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
)


class TrackMixerWidget(QGroupBox):
    """One row per stem: name label, volume slider and mute toggle.

    Volume sliders emit ``volume_changed`` live on ``valueChanged`` and mute
    buttons emit ``muted_changed`` on click. Programmatic updates via
    ``set_track_volume``/``set_track_muted`` are guarded against feedback.
    """

    volume_changed = Signal(str, float)  # name, volume (0.0-1.0)
    muted_changed = Signal(str, bool)  # name, muted

    def __init__(self) -> None:
        super().__init__("Tracks")
        self._rows: dict[str, tuple[QSlider, QPushButton]] = {}
        self._muted: dict[str, bool] = {}
        self._updating = False
        self._layout = QVBoxLayout(self)
        self.setEnabled(False)

    def set_tracks(
        self,
        names: list[str],
        volumes: dict[str, float] | None = None,
        muted: dict[str, bool] | None = None,
    ) -> None:
        """Rebuild the mixer rows from the given track names."""
        self.clear()
        volumes = volumes or {}
        muted = muted or {}
        for name in names:
            self.add_track(name, volumes.get(name, 1.0), muted.get(name, False))
        self.setEnabled(bool(names))

    def add_track(self, name: str, volume: float = 1.0, muted: bool = False) -> None:
        """Add a single track row."""
        row = QHBoxLayout()

        label = QLabel(name)
        label.setMinimumWidth(80)
        row.addWidget(label)

        slider = QSlider(Qt.Horizontal)
        slider.setRange(0, 100)
        slider.setValue(int(volume * 100))
        slider.valueChanged.connect(
            lambda value, track_name=name: self._on_volume_changed(track_name, value)
        )
        row.addWidget(slider, stretch=1)

        button = QPushButton("Mute")
        button.setCheckable(True)
        button.setChecked(muted)
        button.clicked.connect(
            lambda checked, track_name=name: self._on_mute_clicked(track_name, checked)
        )
        row.addWidget(button)

        self._rows[name] = (slider, button)
        self._muted[name] = muted
        self._update_button_text(name)
        self._layout.addLayout(row)

    def remove_track(self, name: str) -> None:
        """Remove a single track row, keeping the remaining state."""
        if name not in self._rows:
            return
        state = {
            track_name: (
                self._rows[track_name][0].value() / 100.0,
                self._muted[track_name],
            )
            for track_name in self._rows
            if track_name != name
        }
        self.clear()
        for track_name, (volume, muted) in state.items():
            self.add_track(track_name, volume, muted)
        self.setEnabled(bool(self._rows))

    def clear(self) -> None:
        """Remove all track rows."""
        while self._layout.count():
            item = self._layout.takeAt(0)
            sub = item.layout()
            if sub is not None:
                while sub.count():
                    sub_item = sub.takeAt(0)
                    widget = sub_item.widget()
                    if widget is not None:
                        widget.deleteLater()
                # Schedule the sub-layout for deletion
                sub.deleteLater()
            else:
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
        self._rows.clear()
        self._muted.clear()

    def set_track_volume(self, name: str, volume: float) -> None:
        """Set a track volume programmatically (no signal emitted)."""
        row = self._rows.get(name)
        if row is None:
            return
        self._updating = True
        row[0].setValue(int(volume * 100))
        self._updating = False

    def set_track_muted(self, name: str, muted: bool) -> None:
        """Set a track mute flag programmatically (no signal emitted)."""
        row = self._rows.get(name)
        if row is None:
            return
        self._updating = True
        row[1].setChecked(muted)
        self._updating = False
        self._muted[name] = muted
        self._update_button_text(name)

    def track_names(self) -> list[str]:
        """Names of all rows in insertion order."""
        return list(self._rows)

    def is_muted(self, name: str) -> bool:
        """Current mute state of a track row."""
        return self._muted.get(name, False)

    # --- Internal handlers ---

    def _on_volume_changed(self, name: str, value: int) -> None:
        """Emit volume_changed when a track slider moves (unless updating)."""
        if self._updating:
            return
        self.volume_changed.emit(name, value / 100.0)

    def _on_mute_clicked(self, name: str, checked: bool) -> None:
        """Emit muted_changed when a mute button is toggled."""
        if self._updating:
            return
        self._muted[name] = checked
        self._update_button_text(name)
        self.muted_changed.emit(name, checked)

    def _update_button_text(self, name: str) -> None:
        """Update the mute button label to reflect current state."""
        row = self._rows.get(name)
        if row is None:
            return
        row[1].setText("Muted" if self._muted.get(name, False) else "Mute")
