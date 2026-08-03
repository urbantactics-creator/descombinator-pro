"""Performance infrastructure: profiling, monitoring, and runtime optimization.

Exports:
- ``ResourceMonitor`` / ``ResourceSnapshot``: psutil-based async sampling.
- ``TorchRuntimeOptimizer``: process-level torch thread/MKL-DNN/autocast tuning.
- ``cpu_profile`` / ``torch_profile_trace``: profiling context managers.
- ``ThermalMonitor`` / ``ThermalState`` / ``ThermalSnapshot``: cross-platform
  CPU/GPU thermal sampling with graceful degradation.
"""

from engine.performance.monitor import ResourceMonitor, ResourceSnapshot
from engine.performance.optimizer import TorchRuntimeOptimizer
from engine.performance.profiler import cpu_profile, torch_profile_trace
from engine.performance.thermal import ThermalMonitor, ThermalSnapshot, ThermalState

__all__ = [
    "ResourceMonitor",
    "ResourceSnapshot",
    "TorchRuntimeOptimizer",
    "cpu_profile",
    "torch_profile_trace",
    "ThermalMonitor",
    "ThermalSnapshot",
    "ThermalState",
]
