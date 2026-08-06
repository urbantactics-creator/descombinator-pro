"""Unit tests for the benchmark regression gate."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from scripts.bench import extract_medians, load_baselines
from scripts.bench.check_regressions import check, check_methodology


@pytest.fixture
def baselines() -> dict[str, dict[str, object]]:
    """Baselines file with measurement metadata and a couple of entries."""
    return {
        "_meta": {
            "min_rounds": 10,
            "max_time": 1.0,
            "warmup": "on",
            "calibration_precision": 3,
        },
        "bench_dummy_fast": {"median_ms": 2.0},
        "bench_dummy_slow": {"median_ms": 100.0},
    }


@pytest.fixture
def methodology() -> dict[str, str]:
    """Methodology matching the ``_meta`` recorded in ``baselines``."""
    return {
        "min_rounds": "10",
        "max_time": "1.0",
        "warmup": "on",
        "calibration_precision": "3",
    }


def _write_result(path: Path, medians: dict[str, float]) -> None:
    """Write a minimal pytest-benchmark JSON result file."""
    benches = [
        {
            "name": f"test_{name}",
            "stats": {"median": median / 1000.0},
        }
        for name, median in medians.items()
    ]
    path.write_text(json.dumps({"benchmarks": benches}))


class TestLoadBaselines:
    def test_loads_meta_and_medians(self, tmp_path: Path) -> None:
        data = {"_meta": {"min_rounds": 10}, "bench_x": {"median_ms": 1.0}}
        path = tmp_path / "baselines.json"
        path.write_text(json.dumps(data))
        loaded = load_baselines(path)
        assert loaded["_meta"]["min_rounds"] == 10
        assert loaded["bench_x"]["median_ms"] == 1.0


class TestCheckMethodology:
    def test_matching_config_is_not_stale(
        self,
        baselines: dict[str, dict[str, object]],
        methodology: dict[str, str],
    ) -> None:
        assert check_methodology(baselines, methodology) is None

    def test_mismatched_rounds_is_stale(
        self,
        baselines: dict[str, dict[str, object]],
        methodology: dict[str, str],
    ) -> None:
        methodology["min_rounds"] = "5"
        error = check_methodology(baselines, methodology)
        assert error is not None
        assert "min_rounds" in error

    def test_missing_meta_is_stale(self, methodology: dict[str, str]) -> None:
        error = check_methodology({}, methodology)
        assert error is not None
        assert "_meta" in error


class TestCheck:
    def test_ok_within_ratio(
        self, tmp_path: Path, baselines: dict[str, dict[str, object]]
    ) -> None:
        result = tmp_path / "result.json"
        _write_result(result, {"bench_dummy_fast": 2.0, "bench_dummy_slow": 110.0})
        assert check(baselines, result, verbose=False) == 0

    def test_regression_fails(
        self, tmp_path: Path, baselines: dict[str, dict[str, object]]
    ) -> None:
        result = tmp_path / "result.json"
        _write_result(result, {"bench_dummy_fast": 2.0, "bench_dummy_slow": 250.0})
        assert check(baselines, result, verbose=False) == 1

    def test_absolute_target_fails(
        self, tmp_path: Path, baselines: dict[str, dict[str, object]]
    ) -> None:
        from scripts.bench.check_regressions import TARGETS_MS

        result = tmp_path / "result.json"
        target = next(iter(TARGETS_MS))
        _write_result(result, {target: TARGETS_MS[target] * 2.0})
        assert check(baselines, result, verbose=False) == 1

    def test_extract_medians_strips_prefix(self, tmp_path: Path) -> None:
        result = tmp_path / "result.json"
        _write_result(result, {"bench_dummy_fast": 2.5})
        data = json.loads(result.read_text())
        medians = extract_medians(data)
        assert medians == {"bench_dummy_fast": 2.5}
