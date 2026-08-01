"""Run a real separation under torch.profiler and export a chrome trace.

Usage::

    python scripts/profiling/profile_torch.py [--out trace.json]

Runs the real htdemucs separation over a 3-minute synthetic song and writes a
``trace.json`` viewable in chrome://tracing or TensorBoard. Skipped gracefully
when torch is not available. Marked ``slow``; not run in CI by default.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path

from loguru import logger

from scripts.profiling import ensure_project_root

ensure_project_root()


async def _run_real_separation(out_path: Path) -> None:
    """Run the real Demucs separator over a 3-minute synthetic song."""
    import numpy as np

    from engine.demucs.config import SeparationConfig
    from engine.demucs.separator import DemucsSeparator
    from engine.performance.profiler import torch_profile_trace

    separator = DemucsSeparator(SeparationConfig())
    await separator.initialize()

    sr = 44_100
    t = np.linspace(0.0, 180.0, sr * 180, endpoint=False, dtype=np.float32)
    audio = (0.5 * np.sin(2 * np.pi * 220.0 * t)).astype(np.float32)

    with torch_profile_trace(out_path):
        result = await separator.separate(audio, sr)
    logger.info(f"Separation complete: {list(result.keys())}")


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Profile separation with torch.profiler"
    )
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/development/performance/reports/trace.json"),
        help="Chrome trace output path",
    )
    args = parser.parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)

    try:
        import torch  # noqa: F401
    except ImportError:
        print("torch not installed; cannot run torch profiling.", file=sys.stderr)
        return 1

    asyncio.run(_run_real_separation(args.out))
    print(f"Trace written to {args.out}")
    print("View with: tensorboard --logdir <dir>  (or chrome://tracing)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
