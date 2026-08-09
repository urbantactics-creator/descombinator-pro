# ADR-003: Pydantic Models for State Management

- **Status:** Accepted
- **Date:** 2026-08-02
- **Deciders:** Project Architect, Python Backend Engineer

## Context

The application needs to manage state across multiple layers: UI state, separation configuration, export settings, and playback state. We need a consistent, type-safe approach to state management.

## Decision

We use **Pydantic `BaseModel`** for all state models and **`enum.Enum`** for state machines:

- `app/models/app_state.py` — `AppState` model with `SeparationStatus` enum
- `app/models/settings_model.py` — `SettingsModel` for user preferences
- `engine/inference/config.py` — `InferenceConfig` with `ModelName`/`DeviceType` enums
- `engine/export/config.py` — `ExportConfig` with `ExportFormat` enum

### Rationale

- **Type safety:** Pydantic validates data at runtime
- **Serialization:** Easy JSON serialization/deserialization
- **Documentation:** Type hints serve as documentation
- **Validation:** Field constraints (e.g., `ge=8000, le=192000` for sample rate)
- **Enum integration:** `StrEnum` for string-backed enums (Python 3.11+)

## Consequences

### Positive

- Runtime validation catches errors early
- Clear data contracts between layers
- Easy to serialize/deserialize for persistence
- IDE autocomplete and type checking

### Negative

- Slight overhead from validation (negligible for this use case)
- Learning curve for Pydantic v2 API


### SettingsModel: `use_enum_values=True`

`SettingsModel` opts into `ConfigDict(use_enum_values=True)` so its `StrEnum` fields
(`default_model`, `default_format`) serialize to their `str` values and accept both
`str` and enum members. This is required because settings can be mutated via `setattr`
(e.g. `update_setting` / `update_settings`) with plain `str` values, which would
otherwise trigger a Pydantic serialization warning on `model_dump()`.

**Convention:** `use_enum_values=True` is applied **only** to `SettingsModel`. The
engine configs (`InferenceConfig`, `ExportConfig`, `SeparationConfig`) deliberately do
**not** use it — the Demucs pipeline reads enum *members* (e.g. `ModelName(str(...))`),
and converting them to `str` would break member access. All comparisons use `StrEnum`
equality (`str == ModelName.X` is `True`), so the `str` storage in `SettingsModel` is safe.

## Alternatives Considered

- **Dataclasses:** Rejected — no runtime validation, no serialization helpers
- **Plain dicts:** Rejected — no type safety, no validation
- **SQLAlchemy models:** Rejected — overkill for in-memory state
