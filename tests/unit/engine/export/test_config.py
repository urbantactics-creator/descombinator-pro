"""Unit tests for engine.export.config — ExportConfig and enums."""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from engine.export.config import ExportConfig, ExportFormat, ExportMetadata


class TestExportFormat:
    def test_values(self) -> None:
        assert ExportFormat.WAV == "wav"
        assert ExportFormat.FLAC == "flac"
        assert ExportFormat.MP3 == "mp3"
        assert ExportFormat.M4A == "m4a"

    def test_count(self) -> None:
        assert len(ExportFormat) == 4


class TestExportConfig:
    def test_defaults(self) -> None:
        cfg = ExportConfig()
        assert cfg.format == ExportFormat.WAV
        assert cfg.sample_rate == 44100
        assert cfg.bit_depth == 16
        assert cfg.bitrate == 192000
        assert cfg.normalize is True
        assert cfg.fade_in == 0.0
        assert cfg.fade_out == 0.0
        assert cfg.metadata is None

    def test_custom_values(self) -> None:
        cfg = ExportConfig(
            format=ExportFormat.MP3,
            sample_rate=48000,
            bit_depth=24,
            bitrate=320000,
            normalize=False,
            fade_in=0.5,
            fade_out=1.0,
        )
        assert cfg.format == ExportFormat.MP3
        assert cfg.sample_rate == 48000
        assert cfg.bit_depth == 24
        assert cfg.bitrate == 320000
        assert cfg.normalize is False
        assert cfg.fade_in == 0.5
        assert cfg.fade_out == 1.0

    def test_sample_rate_too_low(self) -> None:
        with pytest.raises(ValidationError):
            ExportConfig(sample_rate=4000)

    def test_sample_rate_too_high(self) -> None:
        with pytest.raises(ValidationError):
            ExportConfig(sample_rate=200000)

    def test_bit_depth_too_low(self) -> None:
        with pytest.raises(ValidationError):
            ExportConfig(bit_depth=4)

    def test_bit_depth_too_high(self) -> None:
        with pytest.raises(ValidationError):
            ExportConfig(bit_depth=64)

    def test_bitrate_too_low(self) -> None:
        with pytest.raises(ValidationError):
            ExportConfig(bitrate=10000)

    def test_bitrate_too_high(self) -> None:
        with pytest.raises(ValidationError):
            ExportConfig(bitrate=500000)

    def test_fade_in_negative(self) -> None:
        with pytest.raises(ValidationError):
            ExportConfig(fade_in=-1.0)

    def test_fade_out_too_long(self) -> None:
        with pytest.raises(ValidationError):
            ExportConfig(fade_out=15.0)

    def test_serialization_roundtrip(self) -> None:
        cfg = ExportConfig(format=ExportFormat.FLAC, bitrate=256000)
        data = cfg.model_dump()
        restored = ExportConfig(**data)
        assert restored == cfg


class TestExportMetadata:
    def test_all_none(self) -> None:
        m = ExportMetadata()
        assert m.title is None
        assert m.artist is None
        assert m.album is None
        assert m.genre is None

    def test_custom_values(self) -> None:
        m = ExportMetadata(title="Song", artist="Artist", album="Album", genre="Rock")
        assert m.title == "Song"
        assert m.artist == "Artist"
        assert m.album == "Album"
        assert m.genre == "Rock"

    def test_with_config(self) -> None:
        m = ExportMetadata(title="Test")
        cfg = ExportConfig(metadata=m)
        assert cfg.metadata is not None
        assert cfg.metadata.title == "Test"
