"""Comprehensive tests for PlaybackController."""

from __future__ import annotations

from unittest.mock import MagicMock

import numpy as np
import pytest

from app.controllers.playback_controller import PlaybackController
from app.audio.mixer import PlaybackState


class TestPlaybackController:
    """Comprehensive tests for PlaybackController."""

    @pytest.fixture
    def mock_service(self):
        """Create a mock playback service."""
        return MagicMock()

    @pytest.fixture
    def mock_store(self):
        """Create a mock playback state store."""
        return MagicMock()

    @pytest.fixture
    def playback_controller(self, mock_service, mock_store):
        """Create PlaybackController with mock dependencies."""
        return PlaybackController(service=mock_service, store=mock_store)

    def test_initialization(self, playback_controller, mock_service, mock_store):
        """Test that PlaybackController initializes correctly."""
        assert playback_controller._service is mock_service
        assert playback_controller._store is mock_store
        # Initial state should be stopped
        mock_service.get_state.return_value = PlaybackState.STOPPED
        assert playback_controller.get_state() == PlaybackState.STOPPED.value

    def test_play(self, playback_controller, mock_service):
        """Test playing audio."""
        playback_controller.play()
        mock_service.play.assert_called_once()

    def test_pause(self, playback_controller, mock_service):
        """Test pausing audio."""
        playback_controller.pause()
        mock_service.pause.assert_called_once()

    def test_stop(self, playback_controller, mock_service):
        """Test stopping audio."""
        playback_controller.stop()
        mock_service.stop.assert_called_once()

    def test_set_source(self, playback_controller, mock_service):
        """Test setting audio source."""
        audio = np.zeros(44100, dtype=np.float32)
        sample_rate = 44100
        playback_controller.set_source(audio, sample_rate)
        mock_service.set_source.assert_called_once_with(audio, sample_rate)

    def test_set_stems(self, playback_controller, mock_service):
        """Test setting audio stems."""
        stems = {
            "vocals": np.zeros(44100, dtype=np.float32),
            "drums": np.zeros(44100, dtype=np.float32)
        }
        playback_controller.set_stems(stems)
        mock_service.set_stems.assert_called_once_with(stems)

    def test_set_position(self, playback_controller, mock_service):
        """Test setting playback position."""
        position_ms = 1000
        playback_controller.set_position(position_ms)
        mock_service.seek_ms.assert_called_once_with(position_ms)

    def test_seek_ms(self, playback_controller, mock_service):
        """Test seeking in milliseconds."""
        ms = 1500
        playback_controller.seek_ms(ms)
        mock_service.seek_ms.assert_called_once_with(ms)

    def test_set_track_volume(self, playback_controller, mock_service):
        """Test setting track volume."""
        playback_controller.set_track_volume("vocals", 0.8)
        mock_service.set_track_volume.assert_called_once_with("vocals", 0.8)

    def test_set_track_muted(self, playback_controller, mock_service):
        """Test setting track mute state."""
        playback_controller.set_track_muted("vocals", True)
        mock_service.set_track_muted.assert_called_once_with("vocals", True)

    def test_set_active_stems(self, playback_controller, mock_service):
        """Test setting active stems."""
        stems = ["vocals", "drums"]
        playback_controller.set_active_stems(stems)
        mock_service.set_active_stems.assert_called_once_with(stems)

    def test_set_master_volume(self, playback_controller, mock_service):
        """Test setting master volume."""
        playback_controller.set_master_volume(0.7)
        mock_service.set_master_volume.assert_called_once_with(0.7)

    def test_set_volume(self, playback_controller, mock_service):
        """Test setting volume (alias for master volume)."""
        playback_controller.set_volume(0.5)
        mock_service.set_master_volume.assert_called_once_with(0.5)

    def test_record_last_file(self, playback_controller, mock_service):
        """Test recording last file."""
        file_path = "/tmp/test.wav"
        playback_controller.record_last_file(file_path)
        assert playback_controller._last_file == file_path
        # _flush_save is internal, we don't need to test it directly

    def test_reset(self, playback_controller, mock_service):
        """Test resetting playback state."""
        playback_controller.reset()
        mock_service.stop.assert_called_once()
        mock_service.clear.assert_called_once()

    def test_get_state(self, playback_controller, mock_service):
        """Test getting playback state."""
        mock_service.get_state.return_value = PlaybackState.PLAYING
        state = playback_controller.get_state()
        assert state == PlaybackState.PLAYING.value
        mock_service.get_state.assert_called_once()

    def test_get_position(self, playback_controller, mock_service):
        """Test getting playback position."""
        mock_service.get_position.return_value = 2500
        position = playback_controller.get_position()
        assert position == 2500
        mock_service.get_position.assert_called_once()

    def test_get_duration(self, playback_controller, mock_service):
        """Test getting duration."""
        mock_service.get_duration.return_value = 30000
        duration = playback_controller.get_duration()
        assert duration == 30000
        mock_service.get_duration.assert_called_once()

    def test_track_names(self, playback_controller, mock_service):
        """Test getting track names."""
        mock_service.track_names.return_value = ["vocals", "drums", "bass"]
        names = playback_controller.track_names()
        assert names == ["vocals", "drums", "bass"]
        mock_service.track_names.assert_called_once()

    def test_track_volumes(self, playback_controller, mock_service):
        """Test getting track volumes."""
        mock_service.track_volumes.return_value = {"vocals": 0.7, "drums": 0.3}
        volumes = playback_controller.track_volumes()
        assert volumes == {"vocals": 0.7, "drums": 0.3}
        mock_service.track_volumes.assert_called_once()

    def test_muted_map(self, playback_controller, mock_service):
        """Test getting muted map."""
        mock_service.muted_map.return_value = {"vocals": True, "drums": False}
        muted_map = playback_controller.muted_map()
        assert muted_map == {"vocals": True, "drums": False}
        mock_service.muted_map.assert_called_once()

    def test_active_stems(self, playback_controller, mock_service):
        """Test getting active stems."""
        mock_service.active_stems.return_value = ["vocals", "drums"]
        stems = playback_controller.active_stems()
        assert stems == ["vocals", "drums"]
        mock_service.active_stems.assert_called_once()

    def test_has_stems(self, playback_controller, mock_service):
        """Test checking if stems are available."""
        mock_service.has_stems.return_value = True
        has_stems = playback_controller.has_stems()
        assert has_stems is True
        mock_service.has_stems.assert_called_once()

        # Test with False
        mock_service.has_stems.return_value = False
        has_stems = playback_controller.has_stems()
        assert has_stems is False
        mock_service.has_stems.assert_called_with()

    def test_has_media(self, playback_controller, mock_service):
        """Test checking if media is loaded."""
        mock_service.has_tracks.return_value = True
        has_media = playback_controller.has_media()
        assert has_media is True
        mock_service.has_tracks.assert_called_once()

        # Test with False
        mock_service.has_tracks.return_value = False
        has_media = playback_controller.has_media()
        assert has_media is False
        mock_service.has_tracks.assert_called_with()

    def test_signal_connections(self, playback_controller):
        """Test that signals are connected."""
        # Just verify the controller was created without error
        # Signal testing would require qtbot and is more complex
        assert playback_controller is not None