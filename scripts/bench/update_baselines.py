"""Regenerate ``benchmarks/baselines.json`` from a pytest-benchmark result.

Run this any time the benchmark methodology changes (rounds, warmup,
calibration precision) or after an intentional, verified performance change.
It stamps the file with the methodology used so ``check_regressions.py`` can
detect staleness instead of producing false regressions.

Usage::

    pytest benchmarks/ -m "not slow" --benchmark-only \\
        --benchmark-min-rounds=10 --benchmark-max-time=1.0 \\
        --benchmark-warmup=on --benchmark-calibration-precision=3 \\
        --benchmark-json=bench_results.json

    python -m scripts.bench.update_baselines \\
        --result bench_results.json \\
        --baseline benchmarks/baselines.json \\
        --min-rounds 10 --max-time 1.0 --warmup on --calibration-precision 3
"""

import argparse
import json
import sys
from pathlib import Path

from scripts.bench import BASELINE_META_KEY, extract_medians, load_benchmark_json


def build_baselines(
    result_path: Path,
    existing_path: Path,
    methodology: dict[str, str],
) -> dict[str, dict[str, float] | dict[str, str]]:
    """Build a new baselines dict, preserving unseen (e.g. `slow`) entries."""
    existing: dict[str, dict[str, float]] = {}
    if existing_path.exists():
        existing = json.loads(existing_path.read_text(encoding="utf-8"))

    medians = extract_medians(load_benchmark_json(result_path))

    new_baselines: dict[str, dict[str, float] | dict[str, str]] = {
        name: existing.get(name, {}) for name in existing if name != BASELINE_META_KEY
    }
    for name, median_ms in medians.items():
        new_baselines[name] = {"median_ms": round(median_ms, 1)}

    new_baselines[BASELINE_META_KEY] = dict(methodology)
    return new_baselines


def main() -> int:
    parser = argparse.ArgumentParser(description="Regenerate benchmark baselines")
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--min-rounds", required=True)
    parser.add_argument("--max-time", required=True)
    parser.add_argument("--warmup", required=True)
    parser.add_argument("--calibration-precision", required=True)
    args = parser.parse_args()

    methodology = {
        "min_rounds": args.min_rounds,
        "max_time": args.max_time,
        "warmup": args.warmup,
        "calibration_precision": args.calibration_precision,
    }

    new_baselines = build_baselines(args.result, args.baseline, methodology)
    args.baseline.write_text(
        json.dumps(new_baselines, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(f"Wrote {len(new_baselines) - 1} benchmark baselines to {args.baseline}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
