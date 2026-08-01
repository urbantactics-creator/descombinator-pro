"""System resource monitoring via psutil.

The monitor samples CPU and memory of the current process asynchronously so it
never blocks the event loop. The first ``cpu_percent`` sample is primed on
``start()`` because psutil returns ``0.0`` until it has a previous sample to
compare against.
"""

from __future__ import annotations

import asyncio
import time
from collections.abc import Awaitable, Callable
from typing import Any

import psutil
from loguru import logger
from pydantic import BaseModel

SnapshotCallback = Callable[["ResourceSnapshot"], Awaitable[None] | None]


class ResourceSnapshot(BaseModel):
    """A point-in-time sample of process resource usage."""

    timestamp: float
    cpu_percent: float
    rss_bytes: int
    vms_bytes: int
    swap_bytes: int


class ResourceMonitor:
    """Sample process CPU/memory usage asynchronously."""

    def __init__(
        self,
        interval: float = 1.0,
        callback: SnapshotCallback | None = None,
    ) -> None:
        """Initialize the monitor.

        Args:
            interval: Sampling interval in seconds.
            callback: Optional async callback invoked per sample.
        """
        self._interval = interval
        self._callback = callback
        self._process = psutil.Process()
        self._running = False
        self._peak_rss: int = 0
        self._samples: list[ResourceSnapshot] = []

    @property
    def running(self) -> bool:
        """True while the monitor is sampling."""
        return self._running

    @property
    def peak_rss_bytes(self) -> int:
        """Highest resident-set-size observed so far."""
        return self._peak_rss

    @property
    def sample_count(self) -> int:
        """Number of samples collected."""
        return len(self._samples)

    async def start(self) -> None:
        """Start sampling. Idempotent."""
        if self._running:
            return
        # Prime cpu_percent so the first sample is not 0.0.
        await asyncio.to_thread(self._process.cpu_percent)
        self._running = True
        logger.debug("ResourceMonitor started")

    async def stop(self) -> None:
        """Stop sampling. Idempotent."""
        if not self._running:
            return
        self._running = False
        await self.sample()
        logger.debug(f"ResourceMonitor stopped: {self.sample_count} samples")

    async def sample(self) -> ResourceSnapshot:
        """Take a single resource sample."""
        mem: Any = await asyncio.to_thread(self._process.memory_info)
        cpu: float = await asyncio.to_thread(self._process.cpu_percent, None)
        swap: Any = await asyncio.to_thread(psutil.swap_memory)

        snapshot = ResourceSnapshot(
            timestamp=time.monotonic(),
            cpu_percent=cpu,
            rss_bytes=int(mem.rss),
            vms_bytes=int(mem.vms),
            swap_bytes=int(swap.total - swap.free),
        )
        self._samples.append(snapshot)
        self._peak_rss = max(self._peak_rss, snapshot.rss_bytes)
        if self._callback is not None:
            result = self._callback(snapshot)
            if asyncio.iscoroutine(result):
                await result
        return snapshot

    def summary(self) -> str:
        """One-line loguru-friendly summary of peak usage."""
        return (
            f"peak RSS={self._peak_rss / 1e6:.1f} MB, "
            f"samples={self.sample_count}, interval={self._interval}s"
        )
