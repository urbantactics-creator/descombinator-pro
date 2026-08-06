"""Measure application startup time.

Runs ``import main`` in a fresh subprocess N times and reports the median
wall-clock time. The startup gate is ``< 3000 ms``.
"""

from __future__ import annotations

import statistics
import subprocess
import sys
import time
from pathlib import Path

from loguru import logger

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
STARTUP_TARGET_MS = 3000.0


def _measure_single() -> float:
    """Time a single ``import main`` in a subprocess, in milliseconds."""
    code = "import sys; sys.argv = ['main']; import main"
    start = time.perf_counter()
    subprocess.run(
        [sys.executable, "-c", code],
        cwd=PROJECT_ROOT,
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    return (time.perf_counter() - start) * 1000.0


def measure_startup(runs: int = 5) -> dict[str, float]:
    """Measure startup over multiple runs.

    Args:
        runs: Number of subprocess runs.

    Returns:
        Dict with min/median/max/mean milliseconds.
    """
    samples = [_measure_single() for _ in range(runs)]
    return {
        "min_ms": min(samples),
        "median_ms": statistics.median(samples),
        "max_ms": max(samples),
        "mean_ms": statistics.mean(samples),
        "runs": runs,
    }


def main() -> int:
    """Run the startup measurement and report the result."""
    runs = int(sys.argv[1]) if len(sys.argv) > 1 else 5
    logger.info(
        "Measuring startup "
        f"(median of {runs} runs, target < {STARTUP_TARGET_MS:.0f} ms)"
    )
    result = measure_startup(runs)
    for key in ("min_ms", "median_ms", "max_ms", "mean_ms"):
        logger.info(f"{key}: {result[key]:.1f} ms")
    median = result["median_ms"]
    ok = median < STARTUP_TARGET_MS
    logger.info(f"Startup gate: {'PASS' if ok else 'FAIL'} ({median:.1f} ms)")
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
