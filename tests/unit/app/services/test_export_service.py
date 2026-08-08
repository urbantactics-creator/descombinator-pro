"""Unit tests for app.services.export_service — ExportService."""

from pathlib import Path
from unittest.mock import AsyncMock, patch

import numpy as np
import pytest

from app.services.export_service import ExportService
from engine.export.config import ExportConfig, ExportFormat


class TestExportServiceInit:
    def test_default_config(self) -> None:
        svc = ExportService()
        assert svc._config.format == ExportFormat.WAV

    def test_custom_config(self) -> None:
        cfg = ExportConfig(format=ExportFormat.FLAC)
        svc = ExportService(config=cfg)
        assert svc._config.format == ExportFormat.FLAC


class TestExportServiceExportStems:
    @pytest.mark.asyncio
    async def test_export_stems_delegates_to_writer(self, tmp_path: Path) -> None:
        svc = ExportService()
        stems = {"vocals": np.zeros(100, dtype=np.float32)}
        with patch.object(svc._writer, "write", new_callable=AsyncMock) as mock_write:
            mock_write.return_value = {"vocals": tmp_path / "vocals.wav"}
            result = await svc.export_stems(stems, tmp_path)
            mock_write.assert_awaited_once_with(stems, tmp_path)
            assert "vocals" in result


class TestExportServiceUpdateConfig:
    def test_update_config(self) -> None:
        svc = ExportService()
        new_cfg = ExportConfig(format=ExportFormat.MP3, bitrate=320000)
        svc.update_config(new_cfg)
        assert svc._config.format == ExportFormat.MP3
        assert svc._config.bitrate == 320000
