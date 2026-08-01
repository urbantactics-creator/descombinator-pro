---
name: performance-engineer
description: >-
  Performance optimization, profiling, benchmarking, memory management,
  and resource monitoring for the Descombinator Pro application.
license: MIT
metadata:
  category: engineering
  project: descombinator-pro
---

# Performance Engineer

## Responsibilities

- Profile and optimize application performance
- Monitor CPU, memory, and disk I/O usage
- Implement performance benchmarks
- Optimize the separation pipeline for speed
- Ensure responsive UI during processing

## Performance Targets

| Metric | Target |
|--------|--------|
| Separation time (3-min song) | < 30 seconds (CPU), < 10 seconds (GPU) |
| Memory usage | < 4 GB peak |
| UI responsiveness | < 100ms for interactions |
| Startup time | < 3 seconds |
| File load time | < 5 seconds for 100 MB |

## Profiling Tools

| Tool | Purpose |
|------|---------|
| `cProfile` | CPU profiling |
| `memory_profiler` | Memory profiling |
| `py-spy` | Sampling profiler |
| `torch.profiler` | PyTorch profiling |
| `psutil` | System resource monitoring |

## Optimization Strategies

### CPU Optimization

- Use `torch.set_num_threads()` to match CPU cores
- Enable `torch.backends.mkldnn` for Intel CPUs
- Use `torch.inference_mode()` to disable gradient computation
- Batch process multiple files when possible

### Memory Optimization

- Process audio in chunks to reduce memory footprint
- Use memory-mapped files for large audio
- Release GPU memory after processing
- Implement garbage collection hints

### I/O Optimization

- Use async I/O for file operations
- Buffer audio data to reduce disk reads
- Compress intermediate files
- Use SSD for temporary storage

## Benchmarking

### Separation Benchmarks

```python
import time
import torch

def benchmark_separation(model, audio, iterations=10):
    times = []
    for _ in range(iterations):
        start = time.perf_counter()
        with torch.inference_mode():
            result = model(audio)
        times.append(time.perf_counter() - start)
    return {
        "mean": sum(times) / len(times),
        "min": min(times),
        "max": max(times),
    }
```

### Performance Monitoring

- Log processing time per stage
- Track memory usage over time
- Monitor CPU utilization
- Alert on performance degradation
