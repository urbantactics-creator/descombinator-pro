"""Benchmark regression gate for CI.

Reads a committed baselines file and a ``pytest-benchmark`` ``--benchmark-json``
result, compares medians (more robust than means against outliers), and exits
non-zero if any benchmark regressed more than 20% over its baseline or missed a
known absolute target.

Usage::

    python scripts/bench/check_regressions.py \
        --baseline benchmarks/baselines.json \
        --result /tmp/bench.json

A baseline median of ``0.0`` marks a benchmark as "no baseline yet"; it is
skipped (the CI runner writes real values into baselines.json after an
intentional optimization).

Baselines are captured under a specific ``pytest-benchmark`` configuration
(min rounds, max time, warmup, calibration precision). ``baselines.json``
records that configuration under the ``_meta`` key; if the flags used to run
the current benchmarks do not match it, the comparison is invalid and the gate
fails with an explicit "baseline stale" error instead of a false regression.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any

from scripts.bench import (
    REGRESSION_RATIO,
    extract_medians,
    load_baselines,
    load_benchmark_json,
)

# Known absolute performance targets, keyed by benchmark name.
TARGETS_MS: dict[str, float] = {
    "bench_startup_import": 3000.0,
    "bench_playback_set_stems": 100.0,
    "bench_playback_set_track_volume": 100.0,
    "bench_waveform_decimate_100mb": 100.0,
    "bench_real_separation_3min": 30000.0,
}

# pytest-benchmark flags that affect measurements; baselines are only valid
# under the exact same configuration.
CONFIG_KEYS: tuple[str, ...] = (
    "min_rounds",
    "max_time",
    "warmup",
    "calibration_precision",
)


def _fmt_ms(ms: float) -> str:
    return f"{ms:.1f} ms"


def _stale_config(
    baselines: dict[str, dict[str, Any]], config: dict[str, Any]
) -> list[str]:
    """Return config keys that differ from the one used to record baselines."""
    meta = baselines.get("_meta", {})
    stale: list[str] = []
    for key in CONFIG_KEYS:
        recorded = meta.get(key)
        current = config.get(key)
        if recorded != current:
            stale.append(f"{key}: baseline recorded {recorded!r}, running {current!r}")
    return stale


def check(
    baselines: dict[str, dict[str, Any]],
    result_path: Path,
    verbose: bool = True,
    config: dict[str, Any] | None = None,
) -> int:
    """Compare benchmark results against baselines. Returns exit code."""
    result = load_benchmark_json(result_path)
    medians = extract_medians(result)
    failures: list[str] = []
    rows: list[tuple[str, float, float | None, float | None, str]] = []

    for name, median in sorted(medians.items()):
        base: float | None = baselines.get(name, {}).get("median_ms", 0.0)
        status = "ok"
        if base and base > 0.0:
            ratio = median / base
            if ratio > REGRESSION_RATIO:
                failures.append(f"{name}: {ratio:.2f}x baseline (regression > 20%)")
                status = "FAIL"
        target = TARGETS_MS.get(name)
        if target is not None and median > target:
            failures.append(
                f"{name}: {_fmt_ms(median)} exceeds target {_fmt_ms(target)}"
            )
            status = "FAIL"
        rows.append((name, median, base, target, status))

    if verbose:
        print(
            f"{'Benchmark':<38} {'Median':>12} {'Baseline':>12} {'Target':>12}  State"
        )
        print("-" * 84)
        for name, median, base, target, status in rows:
            base_s = _fmt_ms(base) if base and base > 0 else "-"
            target_s = _fmt_ms(target) if target is not None else "-"
            row = (
                f"{name:<38} {_fmt_ms(median):>12} {base_s:>12} "
                f"{target_s:>12}  {status}"
            )
            print(row)

    if failures:
        print("\nPerformance regressions detected:")
        for failure in failures:
            print(f"  - {failure}")
        return 1
    return 0


def _add_config_args(parser: argparse.ArgumentParser) -> None:
    """Add flags mirroring the pytest-benchmark measurement configuration."""
    parser.add_argument(
        "--min-rounds",
        type=int,
        required=True,
        help="pytest-benchmark --benchmark-min-rounds used to run benchmarks",
    )
    parser.add_argument(
        "--max-time",
        type=float,
        required=True,
        help="pytest-benchmark --benchmark-max-time used to run benchmarks",
    )
    parser.add_argument(
        "--warmup",
        type=str,
        required=True,
        help="pytest-benchmark --benchmark-warmup used to run benchmarks",
    )
    parser.add_argument(
        "--calibration-precision",
        type=int,
        required=True,
        help="pytest-benchmark --benchmark-calibration-precision",
    )


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Check benchmark regressions")
    parser.add_argument(
        "--baseline",
        type=Path,
        required=True,
        help="Path to benchmarks/baselines.json",
    )
    parser.add_argument(
        "--result",
        type=Path,
        required=True,
        help="Path to pytest-benchmark --benchmark-json output",
    )
    _add_config_args(parser)
    args = parser.parse_args()

    baselines = load_baselines(args.baseline)
    config: dict[str, Any] = {
        "min_rounds": args.min_rounds,
        "max_time": args.max_time,
        "warmup": args.warmup,
        "calibration_precision": args.calibration_precision,
    }
    stale = _stale_config(baselines, config)
    if stale:
        print("Baselines are stale: measurement configuration changed since they")
        print("were recorded. Regenerate benchmarks/baselines.json under the")
        print("current flags before comparing.")
        for item in stale:
            print(f"  - {item}")
        return 2
    return check(baselines, args.result, config=config)


if __name__ == "__main__":
    sys.exit(main())
