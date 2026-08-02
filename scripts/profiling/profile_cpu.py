"""Run a CPU profile of the separation pipeline with a mock model.

Usage::

    python scripts/profiling/profile_cpu.py [--out reports_dir]

Writes a ``cpu.pstats`` file (viewable with ``snakeviz cpu.pstats``) plus a
text report sorted by cumulative time. Marked ``slow``; not run in CI by
default.
"""

from __future__ import annotations

import argparse
import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock

from loguru import logger

from scripts.profiling import ensure_project_root, env_int

ensure_project_root()

from engine.performance.profiler import cpu_profile  # noqa: E402


async def _run_pipeline() -> None:
    """Exercise the mock separation pipeline over a 3-minute synthetic song."""
    from engine.demucs.config import SeparationConfig
    from engine.demucs.separator import DemucsSeparator

    mock_pipeline = MagicMock()
    mock_pipeline.run = AsyncMock(
        return_value={
            "vocals": MagicMock(),
            "other": MagicMock(),
        }
    )
    separator = DemucsSeparator(SeparationConfig())
    separator._pipeline = mock_pipeline

    sr = 44_100
    samples = sr * 180
    audio = (
        0.5
        * __import__("numpy").sin(
            __import__("numpy").linspace(0, 2 * __import__("numpy").pi * 220, samples)
        )
    ).astype("float32")

    result = await separator.separate(audio, sr)
    assert result is not None


def main() -> int:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="CPU-profile the separation pipeline")
    parser.add_argument(
        "--out",
        type=Path,
        default=Path("docs/development/performance/reports"),
        help="Output directory for the profile",
    )
    parser.add_argument(
        "--seconds",
        type=int,
        default=env_int("PROFILE_SECONDS", 30),
        help="Approximate runtime cap (unused beyond reporting)",
    )
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    pstats_path = args.out / "cpu.pstats"
    report_path = args.out / "cpu_report.txt"

    logger.info(f"Profiling pipeline -> {pstats_path}")
    with cpu_profile(pstats_path):
        asyncio.run(_run_pipeline())

    import pstats

    stats = pstats.Stats(str(pstats_path))
    stats.sort_stats("cumtime")
    with report_path.open("w", encoding="utf-8") as f:
        stats.stream = f  # type: ignore[attr-defined]
        stats.print_stats(40)
    print(f"Wrote {pstats_path} and {report_path}")
    print(f"View interactively: snakeviz {pstats_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
