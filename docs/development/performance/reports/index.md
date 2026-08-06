# Performance Reports

Measured results from Phase 8. Hardware-specific — CI runs are the source of
truth for the regression gate (`baselines.json`), which is committed with real
CI medians (run `30728877133`, merged via PR #4).

## Startup (import main)

CI median (benchmark job, Ubuntu 24.04):

| Metric | Value |
| ------ | ----- |
| median | 1093.8 ms |
| Target | < 3000 ms |
| Status | PASS |

`import main` loads no heavy ML modules (`torch`, `librosa`, `demucs`,
`openunmix` all absent from `sys.modules`).

## CI benchmark medians

From `benchmarks/baselines.json` (real values written by the CI runner):

| Benchmark | Median |
| --------- | ------ |
| bench_startup_import | 1093.8 ms |
| bench_audio_load_1min_wav | 3.6 ms |
| bench_audio_preprocess_3min | 19.2 ms |
| bench_audio_postprocess_1min | 3.3 ms |
| bench_engine_pipeline_3min_mock | 21.9 ms |
| bench_engine_separate_3min_mock | 0.4 ms |
| bench_export_wav_1min | 27.4 ms |
| bench_export_flac_1min | 45.1 ms |
| bench_export_mp3_1min | 506.8 ms |
| bench_export_m4a_1min | 2947.7 ms |
| bench_export_batch_sequential | 107.6 ms |
| bench_export_batch_parallel | 84.1 ms |
| bench_playback_readdata_1min | 17.9 ms |
| bench_playback_set_stems | 0.1 ms |
| bench_playback_set_track_volume | 0.0 ms |
| bench_waveform_decimate_100mb | 2.1 ms |
| bench_real_separation_3min | pending (slow, real model) |

All absolute targets met. MP3/M4A export is dominated by encoder cost (lameenc /
AAC), not the app's I/O.

## CPU / memory / torch reports

- `memory_report.txt` — generated with `scripts/profiling/profile_memory.py`
  (psutil RSS sampling over a 3-min mock pipeline run): peak 133.4 MB, target
  < 4096 MB, status **PASS**.
- `trace.json` — `torch.profiler` chrome trace from
  `scripts/profiling/profile_torch.py` (`slow`, real htdemucs).

Run `scripts/profiling/profile_*.py` to regenerate the artifacts for this
machine and replace the tables above with local numbers.
