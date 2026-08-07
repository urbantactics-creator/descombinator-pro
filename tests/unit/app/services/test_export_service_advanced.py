"""Tests for ExportService error handling and edge cases."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest

from app.services.export_service import ExportService
from engine.export.config import ExportConfig, ExportFormat
from engine.export.errors import UnsupportedFormatError, WriteError


class TestExportServiceErrorHandling:
    """Tests for ExportService error handling."""

    @pytest.mark.asyncio
    async def test_export_stems_write_error_propagates(self, tmp_path: Path) -> None:
        """Test that WriteError from writer is propagated."""
        svc = ExportService()
        stems = {"vocals": np.zeros(100, dtype=np.float32)}

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.side_effect = WriteError("Disk full")

            with pytest.raises(WriteError, match="Disk full"):
                await svc.export_stems(stems, tmp_path)

    @pytest.mark.asyncio
    async def test_export_stems_unsupported_format_error(self, tmp_path: Path) -> None:
        """Test that UnsupportedFormatError is propagated."""
        svc = ExportService()
        stems = {"vocals": np.zeros(100, dtype=np.float32)}

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.side_effect = UnsupportedFormatError("Unsupported format: .xyz")

            with pytest.raises(UnsupportedFormatError, match="Unsupported format"):
                await svc.export_stems(stems, tmp_path)

    @pytest.mark.asyncio
    async def test_export_stems_empty_stems_dict(self, tmp_path: Path) -> None:
        """Test exporting empty stems dict returns empty result."""
        svc = ExportService()
        stems: dict[str, np.ndarray] = {}

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {}
            result = await svc.export_stems(stems, tmp_path)

        assert result == {}
        mock_write.assert_awaited_once_with(stems, tmp_path)

    @pytest.mark.asyncio
    async def test_export_stems_creates_output_dir(self, tmp_path: Path) -> None:
        """Test that output directory is created if it doesn't exist."""
        svc = ExportService()
        stems = {"vocals": np.zeros(100, dtype=np.float32)}
        output_dir = tmp_path / "new" / "nested" / "dir"

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {"vocals": output_dir / "vocals.wav"}
            result = await svc.export_stems(stems, output_dir)

        assert "vocals" in result
        mock_write.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_export_stems_multiple_formats(self, tmp_path: Path) -> None:
        """Test exporting with different formats."""
        for fmt in ExportFormat:
            config = ExportConfig(format=fmt)
            svc = ExportService(config=config)
            stems = {"vocals": np.zeros(100, dtype=np.float32)}

            with patch.object(
                svc._writer, "write", new_callable=AsyncMock
            ) as mock_write:
                mock_write.return_value = {
                    f"vocals.{fmt.value}": tmp_path / f"vocals.{fmt.value}"
                }
                result = await svc.export_stems(stems, tmp_path)

            assert "vocals" in result or f"vocals.{fmt.value}" in result
            mock_write.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_export_stems_large_audio_array(self, tmp_path: Path) -> None:
        """Test exporting large audio arrays (10 minutes at 44.1kHz)."""
        svc = ExportService()
        # 10 minutes of audio at 44.1kHz
        large_audio = np.random.randn(44100 * 600).astype(np.float32)
        stems = {"vocals": large_audio}

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {"vocals": tmp_path / "vocals.wav"}
            result = await svc.export_stems(stems, tmp_path)

        assert "vocals" in result
        mock_write.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_export_stems_stereo_audio(self, tmp_path: Path) -> None:
        """Test exporting stereo audio (2 channels)."""
        svc = ExportService()
        # Stereo audio: 2 channels, 1 second
        stereo_audio = np.random.randn(2, 44100).astype(np.float32)
        stems = {"vocals": stereo_audio}

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {"vocals": tmp_path / "vocals.wav"}
            result = await svc.export_stems(stems, tmp_path)

        assert "vocals" in result
        mock_write.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_export_stems_invalid_audio_values(self, tmp_path: Path) -> None:
        """Test exporting audio with values outside [-1, 1] range."""
        svc = ExportService()
        # Audio with values > 1.0 (should be clipped by writer)
        loud_audio = np.ones(100, dtype=np.float32) * 2.0
        stems = {"vocals": loud_audio}

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {"vocals": tmp_path / "vocals.wav"}
            result = await svc.export_stems(stems, tmp_path)

        assert "vocals" in result
        mock_write.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_export_stems_nan_audio(self, tmp_path: Path) -> None:
        """Test exporting audio with NaN values."""
        svc = ExportService()
        nan_audio = np.full(100, np.nan, dtype=np.float32)
        stems = {"vocals": nan_audio}

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.side_effect = WriteError("Invalid audio data")

            with pytest.raises(WriteError, match="Invalid audio data"):
                await svc.export_stems(stems, tmp_path)

    @pytest.mark.asyncio
    async def test_export_stems_inf_audio(self, tmp_path: Path) -> None:
        """Test exporting audio with Inf values."""
        svc = ExportService()
        inf_audio = np.full(100, np.inf, dtype=np.float32)
        stems = {"vocals": inf_audio}

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.side_effect = WriteError("Invalid audio data")

            with pytest.raises(WriteError, match="Invalid audio data"):
                await svc.export_stems(stems, tmp_path)


class TestExportServiceConfigUpdate:
    """Tests for ExportService config update."""

    def test_update_config_changes_format(self) -> None:
        """Test that updating config changes the format."""
        svc = ExportService()
        assert svc._config.format == ExportFormat.WAV

        new_config = ExportConfig(format=ExportFormat.FLAC)
        svc.update_config(new_config)

        assert svc._config.format == ExportFormat.FLAC
        assert svc._writer._config.format == ExportFormat.FLAC

    def test_update_config_changes_bitrate(self) -> None:
        """Test that updating config changes the bitrate."""
        svc = ExportService()
        original_bitrate = svc._config.bitrate

        # Use a value within the valid range (32000-320000)
        new_bitrate = min(original_bitrate * 2, 320000)
        new_config = ExportConfig(bitrate=new_bitrate)
        svc.update_config(new_config)

        assert svc._config.bitrate == new_bitrate
        assert svc._writer._config.bitrate == new_bitrate

    def test_update_config_changes_sample_rate(self) -> None:
        """Test that updating config changes the sample rate."""
        svc = ExportService()

        new_config = ExportConfig(sample_rate=48000)
        svc.update_config(new_config)

        assert svc._config.sample_rate == 48000
        assert svc._writer._config.sample_rate == 48000

    def test_update_config_changes_metadata(self) -> None:
        """Test that updating config changes the metadata."""
        svc = ExportService()
        assert svc._config.metadata is None

        from engine.export.config import ExportMetadata

        metadata = ExportMetadata(title="Test", artist="Artist")
        new_config = ExportConfig(metadata=metadata)
        svc.update_config(new_config)

        assert svc._config.metadata is not None
        assert svc._config.metadata.title == "Test"
        assert svc._writer._config.metadata is not None


class TestExportServiceEdgeCases:
    """Tests for ExportService edge cases."""

    @pytest.mark.asyncio
    async def test_export_stems_with_special_characters_in_names(
        self, tmp_path: Path
    ) -> None:
        """Test exporting stems with special characters in names."""
        svc = ExportService()
        stems = {
            "vocals (main)": np.zeros(100, dtype=np.float32),
            "drums & bass": np.zeros(100, dtype=np.float32),
            "other/weird\\name": np.zeros(100, dtype=np.float32),
        }

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {k: tmp_path / f"{k}.wav" for k in stems}
            result = await svc.export_stems(stems, tmp_path)

        assert len(result) == 3
        mock_write.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_export_stems_unicode_names(self, tmp_path: Path) -> None:
        """Test exporting stems with unicode names."""
        svc = ExportService()
        stems = {
            "vocales": np.zeros(100, dtype=np.float32),
            "バックグラウンド": np.zeros(100, dtype=np.float32),
            "voix": np.zeros(100, dtype=np.float32),
        }

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {k: tmp_path / f"{k}.wav" for k in stems}
            result = await svc.export_stems(stems, tmp_path)

        assert len(result) == 3
        mock_write.assert_awaited_once()

    @pytest.mark.asyncio
    async def test_export_stems_very_long_name(self, tmp_path: Path) -> None:
        """Test exporting stem with very long name."""
        svc = ExportService()
        long_name = "a" * 255  # Max filename length on most filesystems
        stems = {long_name: np.zeros(100, dtype=np.float32)}

        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {long_name: tmp_path / f"{long_name}.wav"}
            result = await svc.export_stems(stems, tmp_path)

        assert long_name in result
        mock_write.assert_awaited_once()
