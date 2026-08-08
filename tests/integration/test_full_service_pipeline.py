"""Integration tests for full service pipeline: load → separation → export."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

from app.services.export_service import ExportService
from app.services.separation_service import SeparationService
from engine.audio.loader import AudioLoader
from engine.demucs.config import SeparationConfig
from engine.export.config import ExportConfig


@pytest.fixture
def separation_config() -> SeparationConfig:
    return SeparationConfig()


@pytest.fixture
def export_config() -> ExportConfig:
    return ExportConfig()


@pytest.fixture
def mock_separator() -> MagicMock:
    """Mock DemucsSeparator with deterministic output."""
    separator = MagicMock()
    separator.state = MagicMock()  # Mock the state attribute
    separator.state.name = "COMPLETE"
    separator.error = None
    separator.separate_file = AsyncMock(
        return_value={
            "vocals": np.ones(44100, dtype=np.float32) * 0.5,
            "instrumental": np.ones(44100, dtype=np.float32) * 0.3,
        }
    )
    separator.initialize = AsyncMock()
    return separator


@pytest.fixture
def separation_service(separation_config: SeparationConfig) -> SeparationService:
    """Create SeparationService."""
    return SeparationService(separation_config)


@pytest.fixture
def export_service(export_config: ExportConfig) -> ExportService:
    return ExportService(export_config)


@pytest.fixture
def audio_loader() -> AudioLoader:
    return AudioLoader()


class TestFullServicePipeline:
    """Test the full pipeline: audio loading → separation → export."""

    @pytest.mark.asyncio
    async def test_load_separate_export_pipeline_mocked(
        self,
        audio_loader: AudioLoader,
        separation_service: SeparationService,
        export_service: ExportService,
        sample_wav_path: Path,
        tmp_path: Path,
        mock_separator: MagicMock,
    ) -> None:
        """Test full pipeline with mocked separation: load → separate → export."""
        # Step 1: Load audio
        _ = await audio_loader.load(sample_wav_path, sr=44100, mono=True)

        # Step 2: Separate audio into stems
        with patch.object(separation_service, "_separator", mock_separator):
            stems = await separation_service.separate(sample_wav_path)
            assert isinstance(stems, dict)
            assert "vocals" in stems
            assert "instrumental" in stems
            assert isinstance(stems["vocals"], np.ndarray)
            assert isinstance(stems["instrumental"], np.ndarray)
            assert stems["vocals"].shape == stems["instrumental"].shape

        # Step 3: Export stems to files
        output_dir = tmp_path / "exported"
        output_paths = await export_service.export_stems(stems, output_dir)

        # Verify export results
        assert isinstance(output_paths, dict)
        assert "vocals" in output_paths
        assert "instrumental" in output_paths
        assert output_paths["vocals"].exists()
        assert output_paths["instrumental"].exists()

        # Verify files are not empty
        assert output_paths["vocals"].stat().st_size > 0
        assert output_paths["instrumental"].stat().st_size > 0

    @pytest.mark.asyncio
    async def test_pipeline_with_different_stem_counts(
        self,
        audio_loader: AudioLoader,
        separation_service: SeparationService,
        export_service: ExportService,
        sample_wav_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test pipeline with different number of stems."""
        # We need to create a new separation service with a different mock for this test
        mock_sep = MagicMock()
        mock_sep.state = MagicMock()
        mock_sep.state.name = "COMPLETE"
        mock_sep.error = None
        mock_sep.separate_file = AsyncMock(
            return_value={
                "vocals": np.random.randn(22050).astype(np.float32),
                "drums": np.random.randn(22050).astype(np.float32),
                "bass": np.random.randn(22050).astype(np.float32),
                "other": np.random.randn(22050).astype(np.float32),
            }
        )
        mock_sep.initialize = AsyncMock()

        # Create a new service with this specific mock
        service = SeparationService(SeparationConfig())
        with patch.object(service, "_separator", mock_sep):
            # Load audio
            _ = await audio_loader.load(sample_wav_path, sr=22050, mono=True)

            # Separate
            stems = await service.separate(sample_wav_path)
            assert len(stems) == 4
            assert set(stems.keys()) == {"vocals", "drums", "bass", "other"}

            # Export
            output_dir = tmp_path / "multi_stem"
            output_paths = await export_service.export_stems(stems, output_dir)

            # Verify all stems exported
            assert len(output_paths) == 4
            for stem_name in ["vocals", "drums", "bass", "other"]:
                assert output_paths[stem_name].exists()
                assert output_paths[stem_name].stat().st_size > 0

    @pytest.mark.asyncio
    async def test_pipeline_error_handling_in_separation(
        self,
        audio_loader: AudioLoader,
        separation_service: SeparationService,
        export_service: ExportService,
        sample_wav_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test that separation errors are properly propagated."""
        # Create service with error-throwing mock
        mock_sep = MagicMock()
        mock_sep.state = MagicMock()
        mock_sep.state.name = "COMPLETE"
        mock_sep.error = None
        from engine.demucs.errors import ProcessingError

        mock_sep.separate_file = AsyncMock(
            side_effect=ProcessingError("Model inference failed")
        )
        mock_sep.initialize = AsyncMock()

        # Create a new service with this specific mock
        service = SeparationService(SeparationConfig())
        with patch.object(service, "_separator", mock_sep):
            # Load audio (should succeed)
            _ = await audio_loader.load(sample_wav_path, sr=44100, mono=True)

            # Separate should raise the error
            with pytest.raises(ProcessingError, match="Model inference failed"):
                await service.separate(sample_wav_path)

            # Export should not be called due to separation failure
            # (This is implicitly tested by the exception above)

    @pytest.mark.asyncio
    async def test_pipeline_error_handling_in_export(
        self,
        audio_loader: AudioLoader,
        separation_service: SeparationService,
        export_service: ExportService,
        sample_wav_path: Path,
        tmp_path: Path,
    ) -> None:
        """Test that export errors are properly propagated."""
        # We need to create a new separation service with a valid mock for this test
        mock_sep = MagicMock()
        mock_sep.state = MagicMock()
        mock_sep.state.name = "COMPLETE"
        mock_sep.error = None
        mock_sep.separate_file = AsyncMock(
            return_value={
                "vocals": np.random.randn(44100).astype(np.float32),
                "instrumental": np.random.randn(44100).astype(np.float32),
            }
        )
        mock_sep.initialize = AsyncMock()

        # Create a new service with this specific mock
        service = SeparationService(SeparationConfig())
        with patch.object(service, "_separator", mock_sep):
            # Load and separate (should succeed)
            _ = await audio_loader.load(sample_wav_path, sr=44100, mono=True)
            stems = await service.separate(sample_wav_path)
            assert isinstance(stems, dict)
            assert len(stems) == 2

            # Make export fail by providing invalid output directory
            # (e.g., a file instead of directory)
            invalid_output_dir = tmp_path / "invalid_dir"
            invalid_output_dir.write_text("not a directory")

            # Export should fail
            with pytest.raises(OSError):
                await export_service.export_stems(stems, invalid_output_dir)


if __name__ == "__main__":
    pytest.main([__file__])
