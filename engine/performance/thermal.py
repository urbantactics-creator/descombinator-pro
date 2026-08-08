"""Thermal monitoring for CPU and GPU temperature sensors.

Reads temperature data from ``psutil.sensors_temperatures()`` (Linux) and
``nvidia-smi`` (cross-platform). On macOS and Windows where
``psutil.sensors_temperatures()`` returns ``{}``, the monitor gracefully
degrades to reporting ``None`` and defaulting to ``ThermalState.NORMAL``.

Thresholds:

    NORMAL:  CPU < 70 °C, GPU < 80 °C
    WARM:    CPU 70–80 °C, GPU 80–85 °C
    HOT:     CPU 80–90 °C, GPU 85–95 °C
    CRITICAL: CPU > 90 °C, GPU > 95 °C
"""

import asyncio
import subprocess
import sys
from enum import StrEnum

from loguru import logger
from pydantic import BaseModel


class ThermalState(StrEnum):
    """Thermal state machine."""

    NORMAL = "normal"
    WARM = "warm"
    HOT = "hot"
    CRITICAL = "critical"


class ThermalSnapshot(BaseModel):
    """Point-in-time thermal reading."""

    cpu_temp_c: float | None = None
    gpu_temp_c: float | None = None
    state: ThermalState = ThermalState.NORMAL


class ThermalMonitor:
    """Asynchronously sample CPU and GPU temperatures.

    The monitor is designed to be called from async code (separation service,
    resource monitor).  All heavy I/O (psutil, subprocess) runs in threads
    via ``asyncio.to_thread`` so the event loop is never blocked.
    """

    CPU_WARM = 70.0
    CPU_HOT = 80.0
    CPU_CRITICAL = 90.0
    GPU_WARM = 80.0
    GPU_HOT = 85.0
    GPU_CRITICAL = 95.0

    def __init__(self) -> None:
        self._state = ThermalState.NORMAL
        self._original_threads: int | None = None
        self._throttled = False

    @property
    def state(self) -> ThermalState:
        """Current thermal state."""
        return self._state

    async def sample(self) -> ThermalSnapshot:
        """Sample temperatures and update internal state.

        Returns:
            A :class:`ThermalSnapshot` with current readings and state.
        """
        cpu = await self._read_cpu_temp()
        gpu = await self._read_gpu_temp()
        self._state = self._evaluate(cpu, gpu)
        return ThermalSnapshot(
            cpu_temp_c=cpu,
            gpu_temp_c=gpu,
            state=self._state,
        )

    async def check_thresholds(self) -> ThermalState:
        """Sample and return the current thermal state (convenience alias)."""
        snap = await self.sample()
        return snap.state

    async def apply_throttle(self) -> dict[str, int]:
        """Apply throttling actions based on the current thermal state.

        Saves the original thread count before throttling so it can be
        restored later via :meth:`restore_throttle`.

        Returns:
            Dict describing actions taken (e.g. ``{"threads": 1}``).
        """
        snap = await self.sample()
        if snap.state in (ThermalState.HOT, ThermalState.CRITICAL):
            import torch

            if not self._throttled:
                self._original_threads = torch.get_num_threads()
                self._throttled = True
            await asyncio.to_thread(torch.set_num_threads, 1)
            if snap.state == ThermalState.CRITICAL:
                logger.critical(
                    "Thermal CRITICAL: reduced threads, separation should pause"
                )
                return {"threads": 1, "pause": True}
            logger.warning("Thermal throttle: reduced torch threads to 1")
            return {"threads": 1}
        return {}

    async def restore_throttle(self) -> None:
        """Restore original thread count after thermal throttling ends."""
        if self._throttled and self._original_threads is not None:
            import torch

            await asyncio.to_thread(torch.set_num_threads, self._original_threads)
            threads = self._original_threads
            logger.info(f"Thermal throttle released: restored threads to {threads}")
            self._throttled = False
            self._original_threads = None

    @staticmethod
    def _evaluate(cpu: float | None, gpu: float | None) -> ThermalState:
        """Determine thermal state from temperature readings."""
        worst = ThermalState.NORMAL
        if cpu is not None:
            if cpu >= ThermalMonitor.CPU_CRITICAL:
                return ThermalState.CRITICAL
            if cpu >= ThermalMonitor.CPU_HOT:
                worst = ThermalState.HOT
            elif cpu >= ThermalMonitor.CPU_WARM and worst == ThermalState.NORMAL:
                worst = ThermalState.WARM
        if gpu is not None:
            if gpu >= ThermalMonitor.GPU_CRITICAL:
                return ThermalState.CRITICAL
            if gpu >= ThermalMonitor.GPU_HOT:
                worst = max(
                    worst, ThermalState.HOT, key=lambda s: list(ThermalState).index(s)
                )
            elif gpu >= ThermalMonitor.GPU_WARM and worst == ThermalState.NORMAL:
                worst = ThermalState.WARM
        return worst

    @staticmethod
    async def _read_cpu_temp() -> float | None:
        """Read CPU temperature via psutil (Linux) or return None."""
        try:
            import psutil

            temps = await asyncio.to_thread(psutil.sensors_temperatures)
            if not temps:
                return None
            for name in ("coretemp", "k10temp", "cpu_thermal", "acpitz"):
                if name in temps and temps[name]:
                    return float(temps[name][0].current)
            first_key = next(iter(temps))
            if temps[first_key]:
                return float(temps[first_key][0].current)
        except Exception as exc:
            logger.debug(f"CPU temp read failed: {exc}")
        return None

    @staticmethod
    async def _read_gpu_temp() -> float | None:
        """Read GPU temperature via nvidia-smi or return None."""
        if sys.platform == "darwin":
            return None
        try:
            proc = await asyncio.to_thread(
                subprocess.run,
                [
                    "nvidia-smi",
                    "--query-gpu=temperature.gpu",
                    "--format=csv,noheader,nounits",
                ],
                capture_output=True,
                text=True,
                timeout=5,
            )
            if proc.returncode == 0 and proc.stdout.strip():
                return float(proc.stdout.strip().split("\n")[0])
        except FileNotFoundError, subprocess.TimeoutExpired, ValueError:
            pass
        return None
