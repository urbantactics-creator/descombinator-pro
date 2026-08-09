"""Unit tests for app.models.settings_model — SettingsModel."""

import warnings
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

    def test_enum_serializes_to_str_without_warning(self) -> None:
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            data = SettingsModel().model_dump()
        assert data["default_model"] == "htdemucs_ft"
        assert data["default_format"] == "wav"
        json_data = SettingsModel().model_dump(mode="json")
        assert json_data["default_model"] == "htdemucs_ft"
        assert json_data["default_format"] == "wav"

    def test_plain_str_enum_accepted(self) -> None:
        m = SettingsModel(default_model="mdx_extra", default_format="mp3")
        assert m.default_model == "mdx_extra"
        assert m.default_format == "mp3"

    def test_enum_member_accepted(self) -> None:
        m = SettingsModel(
            default_model=ModelName.MDX_EXTRA, default_format=ExportFormat.MP3
        )
        assert m.default_model == "mdx_extra"
        assert m.default_format == "mp3"


class TestSettingsModelExportFields:
    def test_export_field_defaults(self) -> None:
        m = SettingsModel()
        assert m.sample_rate == 44100
        assert m.bit_depth == 16
        assert m.bitrate == 192000
        assert m.normalize is True
        assert m.fade_in == 0.0
        assert m.fade_out == 0.0

    def test_export_field_constraints(self) -> None:
        m = SettingsModel(
            sample_rate=8000,
            bit_depth=32,
            bitrate=320000,
            normalize=False,
            fade_in=10.0,
            fade_out=10.0,
        )
        assert m.sample_rate == 8000
        assert m.bit_depth == 32
        assert m.bitrate == 320000
        assert m.normalize is False
        assert m.fade_in == 10.0
        assert m.fade_out == 10.0

    def test_export_fields_roundtrip(self) -> None:
        m = SettingsModel(
            sample_rate=48000,
            bit_depth=24,
            bitrate=256000,
            normalize=False,
            fade_in=1.5,
            fade_out=2.5,
        )
        restored = SettingsModel(**m.model_dump())
        assert restored.sample_rate == 48000
        assert restored.bit_depth == 24
        assert restored.bitrate == 256000
        assert restored.normalize is False
        assert restored.fade_in == 1.5
        assert restored.fade_out == 2.5
