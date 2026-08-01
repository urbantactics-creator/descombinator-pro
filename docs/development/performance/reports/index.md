# Performance Reports

Measured results from Phase 8. Hardware-specific — CI runs are the source of
truth for the regression gate (`baselines.json`).

## Startup (import main)

Local reference run (ubuntu, x86_64):

| Metric | Value |
| ------ | ----- |
| min | ~1.72 s |
| median | ~1.78 s |
| max | ~1.99 s |
| Target | < 3.0 s |
| Status | PASS |

`import main` loads no heavy ML modules (`torch`, `librosa`, `demucs`,
`openunmix` all absent from `sys.modules`).

## Local benchmark sample (medians)

From a local `--benchmark-json` run:

| Benchmark | Median |
| --------- | ------ |
| bench_audio_load_1min_wav | ~10 ms |
| bench_audio_preprocess_3min | ~73 ms |
| bench_audio_postprocess_1min | ~10 ms |
| bench_engine_pipeline_3min_mock | ~68 ms |
| bench_engine_separate_3min_mock | ~0.4 ms |
| bench_export_wav_1min | ~33 ms |
| bench_export_flac_1min | ~67 ms |
| bench_export_mp3_1min | ~932 ms |
| bench_export_m4a_1min | ~5147 ms |
| bench_export_batch_sequential | ~132 ms |
| bench_export_batch_parallel | ~68 ms |
| bench_playback_readdata_1min | ~20 ms |
| bench_playback_set_stems | ~0.1 ms |
| bench_playback_set_track_volume | ~0.0 ms |
| bench_waveform_decimate_100mb | ~9 ms |
| bench_startup_import | ~1831 ms |

All absolute targets met. MP3/M4A export is dominated by encoder cost (lameenc /
AAC), not the app's I/O.

## CPU / memory / torch reports

- `reports/memory.md` — generated with `mprof`/`memory_profiler` over a 3-min
  pipeline run (`slow`): peak RSS + allocator breakdown (input, model
  activations, output stems).
- `reports/torch.md` — `torch.profiler` breakdown by operator (conv1d /
  transformer) from `profile_torch.py` (`slow`, real htdemucs).

Run `scripts/profiling/profile_*.py` to regenerate the artifacts for this
machine and replace the tables above with local numbers.
