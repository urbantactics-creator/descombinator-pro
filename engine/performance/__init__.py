"""Performance infrastructure: profiling, monitoring, and runtime optimization.

Exports:
- ``ResourceMonitor`` / ``ResourceSnapshot``: psutil-based async sampling.
- ``TorchRuntimeOptimizer``: process-level torch thread/MKL-DNN/autocast tuning.
- ``cpu_profile`` / ``torch_profile_trace``: profiling context managers.
"""

from engine.performance.monitor import ResourceMonitor, ResourceSnapshot
from engine.performance.optimizer import TorchRuntimeOptimizer
from engine.performance.profiler import cpu_profile, torch_profile_trace

__all__ = [
    "ResourceMonitor",
    "ResourceSnapshot",
    "TorchRuntimeOptimizer",
    "cpu_profile",
    "torch_profile_trace",
]
