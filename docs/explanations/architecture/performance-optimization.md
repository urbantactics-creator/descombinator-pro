# Performance Optimization

How Descombinator Pro achieves fast, efficient audio processing.

## Startup Optimization

### Lazy Imports

The application uses lazy imports to achieve fast startup (~1 second). The ML stack (PyTorch, Demucs, etc.) is only loaded when a separation is started.

```python
# Heavy imports are deferred
def start_separation():
    import torch
    import demucs
    # ... load model
```

### Benchmark

| Metric | Target | CI Median |
|--------|--------|-----------|
| Startup import | < 3 s | ~1.09 s |

## Processing Optimization

### Parallel Processing

- **Max workers:** Configurable number of parallel workers (default: CPU count)
- **Chunked processing:** Audio is processed in chunks to limit memory usage

### GPU Acceleration

- Automatically used if CUDA is available
- No user configuration needed

### Memory Management

- Peak memory usage: < 500 MB for a 3-minute song
- Chunked processing prevents OOM errors on large files

## Benchmark Results

CI runs a benchmark regression gate on every PR. Key results:

| Benchmark | CI Median | Target |
|-----------|-----------|--------|
| Startup import | ~1.09 s | < 3 s |
| Playback interactions | < 0.1 ms | < 100 ms |
| Waveform decimation | ~2.1 ms | < 100 ms |
| Memory peak | 133 MB | < 4 GB |

## Thermal Monitoring

The status bar shows CPU/GPU temperature when sensors are available.

- **Normal:** Full speed
- **HOT:** Reduces CPU threads
- **CRITICAL:** Pauses separation

Supported platforms:
- **Linux:** `coretemp`/`k10temp` for CPU, `nvidia-smi` for GPU
- **macOS/Windows:** May not report temperatures; app runs normally

## Profiling

See [Development Guide](../../development/development.md) for profiling instructions.

- CPU profiling with `cProfile` and `py-spy`
- Memory profiling with `memory_profiler`
- PyTorch profiling with `torch.profiler`

## See Also

- [Architecture Overview](overview.md)
- [Separation Engine](separation-engine.md)
- [Development Guide](../../development/development.md)
