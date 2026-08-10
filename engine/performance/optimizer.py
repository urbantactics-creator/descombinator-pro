"""Torch runtime tuning: thread counts, MKL-DNN, and autocast.

The optimizer is a classmethod-only utility that configures the process-level
torch runtime exactly once. The key rule prevents thread oversubscription: when
Demucs runs with multiple ``jobs`` (process workers), each process should use a
single thread so ``threads x processes`` stays near the core count.
"""

import os
from collections.abc import Iterator
from contextlib import contextmanager

from loguru import logger

from engine.inference.config import DeviceType


class TorchRuntimeOptimizer:
    """Configure the torch runtime for the current process."""

    _configured: bool = False

    @classmethod
    def configure(cls, device: DeviceType = DeviceType.CPU, jobs: int = 0) -> None:
        """Apply runtime settings once per process.

        Args:
            device: Compute device to configure for.
            jobs: Number of Demucs process workers. When > 1 each process is
                restricted to a single thread to avoid oversubscription.
        """
        if cls._configured:
            return
        import torch

        if jobs > 1:
            torch.set_num_threads(1)
        else:
            cpu_count = os.cpu_count() or 1
            _workers_env = os.getenv("MAX_WORKERS")
            try:
                if _workers_env is not None:
                    workers = max(1, int(_workers_env))
                else:
                    workers = max(1, cpu_count - 1)
            except ValueError:
                workers = max(1, cpu_count - 1)
            torch.set_num_threads(workers)

        mkldnn = getattr(torch.backends, "mkldnn", None)
        if mkldnn is not None:
            try:
                if mkldnn.is_available():
                    mkldnn.enabled = True
            except Exception as exc:
                logger.debug(f"MKL-DNN enable failed: {exc}")

        cls._configured = True

    @staticmethod
    @contextmanager
    def autocast_ctx(mixed_precision: bool, device: str = "cuda") -> Iterator[None]:
        """Wrap a block in ``torch.autocast`` when enabled.

        Args:
            mixed_precision: Whether autocast is active.
            device: Device type string accepted by ``torch.autocast``.

        Usage::

            with TorchRuntimeOptimizer.autocast_ctx(True, "cuda"):
                run_inference()
        """
        import torch

        with torch.autocast(device_type=device, enabled=mixed_precision):
            yield
