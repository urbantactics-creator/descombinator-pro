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

    import time

    import psutil

    extra_args = ["--real"] if args.real else []
    proc = subprocess.Popen(
        [sys.executable, "-m", "scripts.profiling._mem_runner", *extra_args],
        env={**__import__("os").environ, "PYTHONPATH": "."},
    )
    peak_mb = 0.0
    try:
        while proc.poll() is None:
            try:
                rss = psutil.Process(proc.pid).memory_info().rss
                children = psutil.Process(proc.pid).children(recursive=True)
                for child in children:
                    rss += child.memory_info().rss
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                rss = 0.0
            peak_mb = max(peak_mb, rss / (1024 * 1024))
            time.sleep(args.interval)
    finally:
        proc.wait()
        returncode = proc.returncode

    report = (
        f"Memory profile report\n"
        f"====================\n"
        f"runner: scripts.profiling._mem_runner {' '.join(extra_args)}\n"
        f"interval: {args.interval}s\n"
        f"peak RSS: {peak_mb:.1f} MB ({peak_mb / 1024:.2f} GB)\n"
        f"target:   < 4096 MB (4 GB)\n"
        f"status:   {'PASS' if peak_mb < 4096 else 'FAIL'}\n"
    )
    args.out.write_text(report, encoding="utf-8")
    print(report)
    print(f"Report written to {args.out}")
    if returncode != 0:
        print(f"runner exited with code {returncode}", file=sys.stderr)
        return returncode
    return 0 if peak_mb < 4096 else 1


if __name__ == "__main__":
    sys.exit(main())
