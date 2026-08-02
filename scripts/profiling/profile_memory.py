"""Memory-profile the separation pipeline with memory_profiler.

Usage::

    python scripts/profiling/profile_memory.py [--real] [--interval 0.05]

Samples RSS in a subprocess while the mock (or real) pipeline runs, prints peak
usage, and writes a text report. Alternative manual flow::

    mprof run --include-children scripts/profiling/_mem_runner.py
    mprof plot -o docs/development/performance/reports/memory.png
    mprof report

Target: peak < 4 GB for a 3-minute song. Marked ``slow``; not run in CI.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from scripts.profiling import ensure_project_root

ensure_project_root()


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Memory-profile the separation pipeline"
    )
    parser.add_argument(
        "--real",
        action="store_true",
        help="Run the real model instead of a mock (downloads/loads weights)",
    )
    parser.add_argument(
        "--interval",
        type=float,
        default=0.05,
        help="Sampling interval in seconds",
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/development/performance/reports/memory_report.txt"),
        help="Text report destination",
    )
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)

    runner = ["scripts/profiling/_mem_runner.py"]
    if args.real:
        runner.append("--real")

    code = (
        "import sys, subprocess, json\n"
        "from memory_profiler import memory_usage\n"
        f"args = {runner!r}\n"
        "cmd = [sys.executable, *args]\n"
        f"interval = {args.interval!r}\n"
        "samples = memory_usage(cmd, interval=interval, include_children=True)\n"
        "peak = max(samples) if samples else 0.0\n"
        "print('__PEAK_MB__', peak)\n"
    )
    result = subprocess.run(
        [sys.executable, "-c", code], capture_output=True, text=True
    )
    peak_mb: float = 0.0
    for line in result.stdout.splitlines():
        if line.startswith("__PEAK_MB__"):
            peak_mb = float(line.split()[1])

    report = (
        f"Memory profile report\n"
        f"====================\n"
        f"runner: {' '.join(runner)}\n"
        f"interval: {args.interval}s\n"
        f"peak RSS: {peak_mb:.1f} MB ({peak_mb / 1024:.2f} GB)\n"
        f"target:   < 4096 MB (4 GB)\n"
        f"status:   {'PASS' if peak_mb < 4096 else 'FAIL'}\n"
    )
    args.out.write_text(report, encoding="utf-8")
    print(report)
    print(f"Report written to {args.out}")
    if result.returncode != 0:
        print(result.stderr, file=sys.stderr)
        return result.returncode
    return 0 if peak_mb < 4096 else 1


if __name__ == "__main__":
    sys.exit(main())
