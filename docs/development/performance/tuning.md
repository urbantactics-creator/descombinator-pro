# Performance Tuning

Practical guidance for tuning Descombinator Pro's separation pipeline on a
given machine. Every knob below is either exposed in Settings or driven by an
environment variable; defaults are safe on commodity hardware.

## Threading: `MAX_WORKERS` × Demucs `jobs`

- `MAX_WORKERS` (default: CPU count) maps to `torch.set_num_threads(...)`.
- Demucs `jobs` spawns separate *processes*; when `jobs > 1`,
  `TorchRuntimeOptimizer` drops `torch.set_num_threads(1)` per process to
  avoid oversubscription (threads × processes saturating the cores).

| Scenario | `MAX_WORKERS` | Demucs `jobs` |
| -------- | ------------- | ------------- |
| Single-file interactive UI | CPU count (default) | 0 (default) |
| Batch/CLI with many cores | CPU count | 2–4 |

Rule of thumb: `jobs × threads_per_process ≈ physical cores`.

## MKLDNN (Intel CPU)

`torch.backends.mkldnn` is enabled automatically when available. There is
usually no reason to disable it; on non-Intel CPUs it is a no-op.

## `segment` (Demucs chunking)

`segment` controls how Demucs chunks the input and crossfades between chunks:

- `None` (default): Demucs picks a sensible automatic segment.
- Smaller segments (e.g. 8–16 s) bound peak memory for very long tracks at a
  small quality cost around chunk boundaries.
- Open-Unmix ignores `segment` and processes the full length (documented limit).

Trade-off: lower `segment` → less memory; higher → better crossfade quality.
The quality/memory trade-off is user-selectable in Settings (Advanced).

## Mixed precision & pinned memory (GPU)

Both are only active when `device == cuda`:

- `mixed_precision` enables `torch.autocast("cuda")` (fp16 compute, faster,
  lower VRAM). bfloat16 is supported on CPU but not used by default.
- `pin_memory` pins input tensors for faster CPU→GPU transfers.

These are exposed in Settings (Advanced). They are no-ops on CPU-only machines.

## Cache & temp storage

- `MODEL_CACHE_DIR` (default `~/.cache/descombinator`) stores model weights.
  Point it at an SSD for faster model load.
- The in-memory mixer (Phase 7) writes no temporary audio files; if you set a
  `TMPDIR`, put it on an SSD for any OS temp usage.

## Memory release

`ModelManager.free_memory()` runs `torch.cuda.empty_cache()` (CUDA) plus
`gc.collect()` after separation. `ModelManager.unload_all()` unloads every
cached model and is available for low-memory sessions.

## I/O fast paths

`AudioLoader` picks the cheapest decode per format:

- WAV PCM → `np.memmap` over the data region (no full library decode).
- Other WAV / FLAC / AIFF → `soundfile`.
- MP3 / M4A / OGG → `librosa` fallback.

The UI decodes a file once for the waveform and reuses that buffer via
`SeparationService.separate_loaded` — large files are never decoded twice.

## Verifying your changes

```bash
# Startup gate
.venv/bin/python scripts/profiling/measure_startup.py

# Benchmarks (local, no real model)
xvfb-run -a pytest benchmarks/ -m "not slow" --benchmark-only \
  --benchmark-min-rounds=5 --benchmark-json=/tmp/bench.json

# Full separation (real htdemucs, slow)
.venv/bin/python -m pytest benchmarks/bench_real_separation.py -m slow
```
