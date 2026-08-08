"""CPU and PyTorch profiling helpers.

These context managers intentionally avoid importing profiling libraries at
module scope so importing this module stays cheap; the heavy imports happen
inside the context managers only when profiling is actually requested.
"""

import cProfile
import pstats
from collections.abc import Iterator
from contextlib import contextmanager
from pathlib import Path
from typing import Any


@contextmanager
def cpu_profile(out_path: Path, sort_by: str = "cumtime") -> Iterator[None]:
    """Profile the enclosed block with cProfile and write sorted pstats.

    Args:
        out_path: Destination for the ``pstats`` dump.
        sort_by: pstats sort key (default ``cumtime``).

    Usage::

        with cpu_profile(Path("cpu.pstats")):
            run_pipeline()
    """
    profiler = cProfile.Profile()
    profiler.enable()
    try:
        yield
    finally:
        profiler.disable()
        profiler.dump_stats(str(out_path))
        stats = pstats.Stats(profiler)
        stats.sort_stats(sort_by)
        stats.print_stats()


@contextmanager
def torch_profile_trace(out_path: Path) -> Iterator[None]:
    """Profile the enclosed block with torch.profiler.

    Writes a chrome-tracing JSON file. The torch import is lazy so the helper
    remains usable on systems without torch.

    Args:
        out_path: Destination for the ``trace.json`` output.

    Usage::

        with torch_profile_trace(Path("trace.json")):
            run_inference()
    """
    import torch

    activities: list[Any] = [torch.profiler.ProfilerActivity.CPU]
    if torch.cuda.is_available():
        activities.append(torch.profiler.ProfilerActivity.CUDA)

    profile = torch.profiler.profile(
        activities=activities,
        profile_memory=True,
        with_stack=False,
    )
    profile.start()
    try:
        yield
    finally:
        profile.stop()
        profile.export_chrome_trace(str(out_path))
