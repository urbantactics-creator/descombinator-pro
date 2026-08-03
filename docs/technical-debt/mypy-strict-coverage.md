# Mypy Strict Coverage Debt Tracker

## Status

`mypy --strict` passes in CI, but `[[tool.mypy.overrides]]` in `pyproject.toml` sets `ignore_errors = true` for **28 of 44** business-logic modules in `app/` and `engine/` (~64%).

The override comment says: *"Pre-existing drift (Phase 6/7-era): Qt enum/attr typing gaps and untyped mutagen calls. Kept out of the Phase 8 scope."*

## Goal

Bring all excluded modules into mypy strict compliance. Remove `ignore_errors = true` per module and ensure `mypy --strict` passes cleanly.

## Checklist

### app/ layer (17 modules)

- [ ] `app/ui/main_window.py`
- [ ] `app/ui/processing_dialog.py`
- [ ] `app/ui/settings_dialog.py`
- [ ] `app/widgets/file_drop_zone.py`
- [ ] `app/widgets/playback_controls.py`
- [ ] `app/widgets/progress_bar.py`
- [ ] `app/widgets/track_mixer.py`
- [ ] `app/widgets/track_selector.py`
- [ ] `app/widgets/waveform_view.py`
- [ ] `app/audio/mixer.py`
- [ ] `app/controllers/settings_controller.py`
- [ ] `app/controllers/main_controller.py`
- [ ] `app/controllers/playback_controller.py`
- [ ] `app/services/playback_service.py`
- [ ] `app/models/settings_model.py`
- [ ] `app/models/app_state.py`
- [ ] `app/workers/audio_load_worker.py`

### engine/ layer (11 modules)

- [ ] `engine/audio/metadata.py`
- [ ] `engine/audio/postprocessor.py`
- [ ] `engine/audio/resampler.py`
- [ ] `engine/demucs/config.py`
- [ ] `engine/demucs/separator.py`
- [ ] `engine/export/config.py`
- [ ] `engine/export/metadata.py`
- [ ] `engine/export/writer.py`
- [ ] `engine/inference/config.py`
- [ ] `engine/inference/pipeline.py`
- [ ] `engine/performance/monitor.py`

### Test modules (separate concern)

- [ ] `tests/ui/*`
- [ ] `tests/unit/app/widgets/*`
- [ ] `tests/unit/app/audio/*`
- [ ] `tests/unit/app/controllers/*`
- [ ] `tests/unit/app/services/*`
- [ ] `tests/unit/engine/export/*`
- [ ] `tests/unit/engine/inference/*`
- [ ] `tests/unit/engine/performance/*`
- [ ] `tests/unit/engine/audio/test_metadata`
- [ ] `tests/integration/test_separator`
- [ ] `tests/integration/test_export_pipeline`
- [ ] `tests/integration/test_full_pipeline`

## Notes

- The override list has duplicate entries (e.g., `engine.inference.config`, `app.models.settings_model`) that should be deduplicated when cleaning up.
- Dev tooling (`benchmarks.*`, `scripts.*`) is intentionally excluded and should remain.
- Third-party stubs (`torch.*`, `PySide6.*`, etc.) use `ignore_missing_imports` and are not part of this effort.
