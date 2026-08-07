"""Unit tests for app.models.settings_model — SettingsModel."""

from __future__ import annotations

from pathlib import Path

from app.models.settings_model import SettingsModel
from engine.export.config import ExportFormat
from engine.inference.config import ModelName


class TestSettingsModelDefaults:
    def test_default_output_dir(self) -> None:
        m = SettingsModel()
        assert m.output_dir == Path.home() / "Music" / "Descombinator"

    def test_default_model(self) -> None:
        m = SettingsModel()
        assert m.default_model == ModelName.HTDEMUCS_FT

    def test_default_format(self) -> None:
        m = SettingsModel()
        assert m.default_format == ExportFormat.WAV

    def test_default_theme(self) -> None:
        m = SettingsModel()
        assert m.theme == "dark"

    def test_default_segment(self) -> None:
        m = SettingsModel()
        assert m.segment is None

    def test_default_mixed_precision(self) -> None:
        m = SettingsModel()
        assert m.mixed_precision is False

    def test_default_pin_memory(self) -> None:
        m = SettingsModel()
        assert m.pin_memory is False


class TestSettingsModelAccessibility:
    def test_defaults_reduced_motion_false(self) -> None:
        m = SettingsModel()
        assert m.reduced_motion is False

    def test_defaults_high_contrast_false(self) -> None:
        m = SettingsModel()
        assert m.high_contrast is False

    def test_model_dump_includes_accessibility(self) -> None:
        m = SettingsModel(reduced_motion=True, high_contrast=True)
        data = m.model_dump()
        assert data["reduced_motion"] is True
        assert data["high_contrast"] is True
        restored = SettingsModel(**data)
        assert restored.reduced_motion is True
        assert restored.high_contrast is True


class TestSettingsModelCustom:
    def test_custom_values(self) -> None:
        m = SettingsModel(
            output_dir=Path("/tmp/out"),
            default_model=ModelName.MDX_EXTRA,
            default_format=ExportFormat.MP3,
            theme="light",
            segment=30,
            mixed_precision=True,
            pin_memory=True,
        )
        assert m.output_dir == Path("/tmp/out")
        assert m.default_model == ModelName.MDX_EXTRA
        assert m.default_format == ExportFormat.MP3
        assert m.theme == "light"
        assert m.segment == 30
        assert m.mixed_precision is True
        assert m.pin_memory is True


class TestSettingsModelSerialization:
    def test_to_dict(self) -> None:
        m = SettingsModel()
        data = m.model_dump()
        assert "output_dir" in data
        assert "default_model" in data
        assert "theme" in data

    def test_roundtrip(self) -> None:
        m = SettingsModel(theme="light", segment=60)
        data = m.model_dump()
        restored = SettingsModel(**data)
        assert restored.theme == "light"
        assert restored.segment == 60
