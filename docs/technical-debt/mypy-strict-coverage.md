# Mypy Strict Coverage Debt Tracker

## Status

`mypy --strict` passes cleanly in CI (**0 issues across 155 source files**, CI run #45, commit `094a3f9`). CI also excludes `build/`, `dist/`, and `.venv/` from the type-check surface (commit `4e04936`).

However, `[[tool.mypy.overrides]]` in `pyproject.toml` sets `ignore_errors = true` for the app/engine business-logic modules listed below. The override comment says: *"Pre-existing drift (Phase 6/7-era): Qt enum/attr typing gaps and untyped mutagen calls. Kept out of the Phase 8 scope; see PR #4 description."* Phase 9 added overrides for `tests.unit.engine.demucs.*`, `tests.unit.engine.audio.test_errors`, and `tests.unit.app.models.*`; `engine/performance/thermal.py` and `engine/performance/profiler.py` are written strict and are NOT in the overrides.

## Configuration Notes

- The strict-mode overrides live in `pyproject.toml` under `[tool.mypy]` / `[[tool.mypy.overrides]]`:
  - One override block sets `ignore_missing_imports = true` for third-party stubs (`torch.*`, `PySide6.*`, etc.) — this is expected and permanent.
  - One override block sets `ignore_errors = true` for dev tooling (`benchmarks.*`, `scripts.*`) — intentional.
  - One override block sets `ignore_errors = true` for pre-existing Phase 6/7-era drift in `app/` and `engine/` plus test modules — this is the debt tracked here.
- Mypy runs with `exclude = ["^build/", "^dist/", "^\\.venv/"]` so packaging artifacts never gate the type-check.
- The override list contains duplicate entries (e.g., `engine.inference.config`, `engine.export.config`, `engine.demucs.config`, `app.models.settings_model`, `app.models.app_state`, `engine.performance.monitor`) that should be deduplicated when cleaning up.
- CI command: `mypy .` (must stay clean). Local verification: `source activate.sh && mypy .`

## Goal

Bring all excluded modules into mypy strict compliance. Remove `ignore_errors = true` per module and ensure `mypy --strict` passes cleanly.

## Checklist

### app/ layer

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

### engine/ layer

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
