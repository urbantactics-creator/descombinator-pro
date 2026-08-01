# Performance Optimization Guide

Descombinator Pro's Phase 8 performance work: profiling tooling, the
`engine/performance/` package, benchmarks, and the CI regression gate.

## Performance Targets

| Metric | Target | Gate |
| ------ | ------ | ---- |
| Separation time (3-min song, CPU) | < 30 s | `bench_real_separation_3min` (`slow`) |
| Separation time (3-min song, GPU) | < 10 s | manual/CI with CUDA (guarded code) |
| Memory peak | < 4 GB | `scripts/profiling/profile_memory.py` (`slow`) |
| UI responsiveness | < 100 ms | `bench_playback_*` |
| Startup time | < 3 s | `bench_startup_import` / `measure_startup.py` |
| File load time (100 MB) | < 5 s | WAV-PCM memmap fast path |

## Profiling

### CPU profiling (cProfile)

`engine/performance/profiler.py` exposes a `cpu_profile(out_path)` context
manager that runs `cProfile` and writes `pstats` output sorted by cumulative
time. Run a separation against the mock pipeline:

```bash
.venv/bin/python scripts/profiling/profile_cpu.py
.venv/bin/python -m snakeviz <pstats-output>
```

Typical hotspots to look for: `DemucsAgent.separate_tensor`, pre/postprocess
numpy ops, and tensor↔numpy conversion in `InferencePipeline.run`.

### CPU profiling (py-spy)

Sampling profiler — no code instrumentation, works on a running process:

```bash
# Terminal 1: start the real separation
.venv/bin/python scripts/profiling/profile_pyspy.py   # spawns the subprocess
# Terminal 2: attach (or let the script drive py-spy)
py-spy record --pid <PID> -o cpu.svg --duration 60
py-spy top --pid <PID>
```

### Memory profiling

`memory_profiler` samples RSS over time in a subprocess (no `@profile`
decorators in source):

```bash
.venv/bin/python scripts/profiling/profile_memory.py
mprof run .venv/bin/python scripts/profiling/_mem_runner.py
mprof plot -o reports/memory.png
```

Target: < 4 GB peak for a 3-minute song.

### PyTorch profiling

`torch_profile_trace(out_path)` context manager exports a Chrome trace
(`torch.profiler`, CPU + CUDA when available, `profile_memory=True`):

```bash
.venv/bin/python scripts/profiling/profile_torch.py   # real htdemucs, slow
# open the trace.json in chrome://tracing or tensorboard
```

## System Resource Monitoring

`engine/performance/monitor.py` provides `ResourceMonitor` (async, psutil-based):

```python
monitor = ResourceMonitor(interval=1.0)
await monitor.start()
try:
    ...
finally:
    await monitor.stop()
    logger.info(monitor.summary())
```

`SeparationService` accepts an optional `monitor=` and logs a peak-RSS summary
around every separation.

## Lazy Imports & Startup

The < 3 s startup gate is achieved by never importing the ML stack until a
separation actually starts:

- PEP 562 `__getattr__` re-exports in `engine/{inference,demucs,audio,export}/__init__.py`.
- Function-local `import torch` / `import librosa` / `import demucs` /
  `import openunmix` inside the methods that need them.

Verify with:

```bash
.venv/bin/python scripts/profiling/measure_startup.py
.venv/bin/python -m pytest tests/unit/test_startup_imports.py
```

## Benchmarks

The `benchmarks/` package uses `pytest-benchmark` (medians, robust to outliers).
Run them locally:

```bash
xvfb-run -a pytest benchmarks/ -m "not slow" --benchmark-only \
  --benchmark-min-rounds=5 --benchmark-calibration-precision=3 \
  --benchmark-json=/tmp/bench.json
python scripts/bench/check_regressions.py \
  --baseline benchmarks/baselines.json --result /tmp/bench.json
```

`baselines.json` is committed; update it only after an intentional
optimization. CI runs the same command in the `benchmark` job and fails the
PR on > 20 % regression over a baseline median or a missed absolute target.

See `docs/development/performance/tuning.md` for knob-by-knob tuning guidance.
