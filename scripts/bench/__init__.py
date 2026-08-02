"""Shared regression-checking helpers for benchmark results."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

REGRESSION_RATIO: float = 1.2

# Key under which baselines.json stores the pytest-benchmark methodology used
# to produce its median_ms values (rounds/warmup/calibration). Comparing
# medians captured under different measurement settings produces false
# regressions, so this must match the settings the "Run benchmarks" step uses.
BASELINE_META_KEY = "_meta"


def load_baselines(path: Path) -> dict[str, dict[str, float]]:
    """Load the committed baselines file (bench_name -> {median_ms}).

    The special ``_meta`` key (if present) holds the benchmark methodology
    baselines.json was generated with, and is returned as part of the dict
    under ``BASELINE_META_KEY`` so callers can validate freshness; it is not a
    benchmark entry.
    """
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, dict[str, float]] = json.load(f)
    return data


def load_benchmark_json(path: Path) -> dict[str, Any]:
    """Load a pytest-benchmark ``--benchmark-json`` result file."""
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = json.load(f)
        return data


def extract_medians(result: dict[str, Any]) -> dict[str, float]:
    """Map benchmark name -> median in milliseconds.

    pytest-benchmark writes ``benchmarks`` as a list of per-benchmark dicts;
    some formats use a mapping keyed by name. The ``test_`` prefix is stripped
    to keep results aligned with ``baselines.json`` and the known-targets map.
    """
    benches = result.get("benchmarks", {})
    items = benches.values() if isinstance(benches, dict) else benches
    medians: dict[str, float] = {}
    for item in items:
        raw_name = item.get("name", "")
        name = raw_name[len("test_") :] if raw_name.startswith("test_") else raw_name
        stats = item.get("stats", {})
        median = stats.get("median")
        if name and median is not None:
            # pytest-benchmark reports stats in seconds.
            medians[name] = float(median) * 1000.0
    return medians
