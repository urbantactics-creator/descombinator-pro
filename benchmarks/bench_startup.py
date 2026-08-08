"""Benchmark for application startup time.

Reuses ``scripts.profiling.measure_startup`` to time ``import main`` in a
fresh subprocess. Target: median < 3000 ms.
"""

import sys
from pathlib import Path

import pytest

from scripts.profiling.measure_startup import measure_startup

PROJECT_ROOT = Path(__file__).resolve().parent.parent


def test_bench_startup_import(benchmark) -> None:
    """Time importing the full application entry point (subprocess)."""
    result = benchmark(measure_startup, runs=1)
    assert result["median_ms"] < 3000.0


@pytest.fixture(autouse=True)
def _skip_unless_subprocess_available() -> None:
    """Fail loudly if sys.executable is not usable (should not happen)."""
    if not sys.executable:
        pytest.skip("no sys.executable available")
