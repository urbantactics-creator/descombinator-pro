"""Benchmark GUI animation overhead during separation workload.

Measures CPU/wall time for Qt animation ticks to ensure they remain
negligible compared to the actual separation work. Animations should
consume < 50 ms for 500 ticks (< 5% of a 1-second simulated separation).
"""

from __future__ import annotations

import time

import pytest
from PySide6.QtWidgets import QApplication

from app.ui.processing_dialog import ProcessingDialog
from app.widgets.file_drop_zone import FileDropZone

N_TICKS = 500
MAX_WALL_MS = 50.0
MAX_CPU_MS = 50.0


@pytest.fixture(scope="session")
def qapp() -> QApplication:
    """Session-scoped QApplication for benchmark widgets."""
    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    yield app


@pytest.fixture(scope="session")
def processing_dialog(qapp: QApplication) -> ProcessingDialog:
    """Create a ProcessingDialog with animations started."""
    dialog = ProcessingDialog()
    dialog._start_animation()
    yield dialog
    dialog._stop_animations()
    dialog.deleteLater()


@pytest.fixture(scope="session")
def file_drop_zone(qapp: QApplication) -> FileDropZone:
    """Create a FileDropZone with animations set up."""
    zone = FileDropZone()
    yield zone
    zone.deleteLater()


def _measure_animation_overhead(
    dialog: ProcessingDialog,
    drop_zone: FileDropZone,
    ticks: int = N_TICKS,
) -> tuple[float, float]:
    """Run N animation ticks and return (wall_seconds, cpu_seconds)."""
    wall_start = time.perf_counter()
    cpu_start = time.process_time()

    for i in range(ticks):
        dialog._rotate_icon()
        dialog._progress_bar.setValue((i * 2) % 101)

        if i % 2 == 0:
            drop_zone._apply_drag_style(True, valid=True)
        else:
            drop_zone._apply_drag_style(False)

    wall_end = time.perf_counter()
    cpu_end = time.process_time()

    return wall_end - wall_start, cpu_end - cpu_start


def test_bench_animation_overhead_500_ticks(
    benchmark,
    processing_dialog: ProcessingDialog,
    file_drop_zone: FileDropZone,
) -> None:
    """GUI animation overhead for 500 ticks (icon + progress + drag states).

    Asserts animation overhead is negligible relative to a 1-second separation
    workload: < 50 ms total wall/CPU time for 500 ticks.
    """

    def _run() -> None:
        wall_s, cpu_s = _measure_animation_overhead(
            processing_dialog, file_drop_zone, ticks=N_TICKS
        )
        wall_ms = wall_s * 1000
        cpu_ms = cpu_s * 1000
        assert wall_ms < MAX_WALL_MS, (
            f"Animation wall overhead too high: {wall_ms:.1f} ms "
            f"(limit {MAX_WALL_MS} ms)"
        )
        assert cpu_ms < MAX_CPU_MS, (
            f"Animation CPU overhead too high: {cpu_ms:.1f} ms (limit {MAX_CPU_MS} ms)"
        )

    benchmark(_run)
