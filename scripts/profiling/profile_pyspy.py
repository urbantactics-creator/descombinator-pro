"""Launch a real separation in a subprocess and sample it with py-spy.

Usage::

    python scripts/profiling/profile_pyspy.py [--duration 60] [--out cpu.svg]

Runs the actual Demucs separator on a short synthetic song inside a child
process, then runs ``py-spy record`` against that PID. Also prints a live
``py-spy top`` snippet to the console. Requires py-spy on PATH.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

from scripts.profiling import ensure_project_root

ensure_project_root()


def _build_child_cmd() -> list[str]:
    """Command that performs a real separation in a fresh process."""
    return [
        sys.executable,
        "-c",
        (
            "import asyncio, numpy as np\n"
            "from engine.demucs.config import SeparationConfig\n"
            "from engine.demucs.separator import DemucsSeparator\n"
            "async def main():\n"
            "    sep = DemucsSeparator(SeparationConfig())\n"
            "    await sep.initialize()\n"
            "    sr = 44100\n"
            "    audio = "
            "(0.5*np.sin(np.linspace(0, 2*np.pi*220, sr*30))).astype(np.float32)\n"
            "    await sep.separate(audio, sr)\n"
            "asyncio.run(main())\n"
        ),
    ]


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="Sample a separation with py-spy")
    parser.add_argument(
        "--duration", type=int, default=60, help="py-spy record duration (s)"
    )
    parser.add_argument(
        "--out", type=Path, default=Path("docs/development/performance/reports/cpu.svg")
    )
    parser.add_argument(
        "--skip-record",
        action="store_true",
        help="Only show py-spy top, do not write a flamegraph",
    )
    args = parser.parse_args()

    args.out.parent.mkdir(parents=True, exist_ok=True)

    child = subprocess.Popen(_build_child_cmd())
    try:
        time.sleep(3)
        if args.skip_record:
            subprocess.run(
                [
                    "py-spy",
                    "top",
                    "--pid",
                    str(child.pid),
                    "--duration",
                    str(min(args.duration, 10)),
                ]
            )
        else:
            subprocess.run(
                [
                    "py-spy",
                    "record",
                    "--pid",
                    str(child.pid),
                    "--output",
                    str(args.out),
                    "--duration",
                    str(args.duration),
                ]
            )
            print(f"Flamegraph written to {args.out}")
    except FileNotFoundError:
        print(
            "py-spy not found on PATH. Install with: pip install py-spy",
            file=sys.stderr,
        )
        return 1
    finally:
        child.terminate()
        child.wait(timeout=10)
    return 0


if __name__ == "__main__":
    sys.exit(main())
