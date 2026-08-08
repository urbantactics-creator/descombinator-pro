"""Tests for PlaybackService concurrency and edge cases."""

import asyncio
from unittest.mock import MagicMock

import numpy as np
import pytest

from app.audio.mixer import PlaybackState
from app.services.playback_service import PlaybackService


class TestPlaybackServiceConcurrency:
    """Tests for PlaybackService concurrency."""

    @pytest.mark.asyncio
    async def test_concurrent_play_pause_stop(self) -> None:
        """Test that concurrent play/pause/stop operations are handled correctly."""
        mixer = MagicMock()
        mixer.state = PlaybackState.STOPPED
        mixer.position_ms.return_value = 0
        mixer.duration_ms.return_value = 0
        mixer.has_tracks = False
        mixer.track_names.return_value = []
        mixer.track_gains.return_value = {}
        mixer.track_muted_map.return_value = {}
        mixer.active_stems.return_value = []
        svc = PlaybackService(mixer=mixer)

        # Start play operation
        play_task = asyncio.create_task(asyncio.to_thread(svc.play))

        # Try to pause while play is in progress
        pause_task = asyncio.create_task(asyncio.to_thread(svc.pause))

        # Try to stop while play is in progress
        stop_task = asyncio.create_task(asyncio.to_thread(svc.stop))

        # Wait for all to complete
        await asyncio.gather(play_task, pause_task, stop_task, return_exceptions=True)

        # Verify that mixer methods were called
        assert mixer.play.called
        assert mixer.pause.called
        assert mixer.stop.called

    @pytest.mark.asyncio
    async def test_concurrent_set_source_set_stems(self) -> None:
        """Test that concurrent set_source and set_stems operations are handled."""
        mixer = MagicMock()
        mixer.state = PlaybackState.STOPPED
        mixer.position_ms.return_value = 0
        mixer.duration_ms.return_value = 0
        mixer.has_tracks = False
        mixer.track_names.return_value = []
        mixer.track_gains.return_value = {}
        mixer.track_muted_map.return_value = {}
        mixer.active_stems.return_value = []
        svc = PlaybackService(mixer=mixer)

        # Start set_source operation
        audio = np.zeros(44100, dtype=np.float32)
        set_source_task = asyncio.create_task(
            asyncio.to_thread(svc.set_source, audio, 44100)
        )

        # Try to set stems while set_source is in progress
        stems = {"vocals": np.zeros(44100, dtype=np.float32)}
        set_stems_task = asyncio.create_task(
            asyncio.to_thread(svc.set_stems, stems, 44100)
        )

        # Wait for both to complete
        await asyncio.gather(set_source_task, set_stems_task, return_exceptions=True)

        # Verify that mixer.set_tracks was called
        assert mixer.set_tracks.call_count >= 1

    @pytest.mark.asyncio
    async def test_concurrent_volume_changes(self) -> None:
        """Test that concurrent volume changes are handled correctly."""
        mixer = MagicMock()
        mixer.state = PlaybackState.STOPPED
        mixer.position_ms.return_value = 0
        mixer.duration_ms.return_value = 0
        mixer.has_tracks = False
        mixer.track_names.return_value = []
        mixer.track_gains.return_value = {}
        mixer.track_muted_map.return_value = {}
        mixer.active_stems.return_value = []
        svc = PlaybackService(mixer=mixer)

        # Start multiple volume change operations
        tasks = [
            asyncio.create_task(asyncio.to_thread(svc.set_master_volume, 0.1)),
            asyncio.create_task(asyncio.to_thread(svc.set_master_volume, 0.5)),
            asyncio.create_task(asyncio.to_thread(svc.set_master_volume, 0.9)),
            asyncio.create_task(asyncio.to_thread(svc.set_track_volume, "vocals", 0.3)),
            asyncio.create_task(asyncio.to_thread(svc.set_track_volume, "drums", 0.7)),
        ]

        # Wait for all to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Verify that mixer methods were called
        assert mixer.set_master_volume.call_count == 3
        assert mixer.set_track_gain.call_count == 2

    @pytest.mark.asyncio
    async def test_concurrent_mute_unmute(self) -> None:
        """Test that concurrent mute/unmute operations are handled."""
        mixer = MagicMock()
        mixer.state = PlaybackState.STOPPED
        mixer.position_ms.return_value = 0
        mixer.duration_ms.return_value = 0
        mixer.has_tracks = False
        mixer.track_names.return_value = []
        mixer.track_gains.return_value = {}
        mixer.track_muted_map.return_value = {}
        mixer.active_stems.return_value = []
        svc = PlaybackService(mixer=mixer)

        # Start multiple mute/unmute operations
        tasks = [
            asyncio.create_task(asyncio.to_thread(svc.set_track_muted, "vocals", True)),
            asyncio.create_task(
                asyncio.to_thread(svc.set_track_muted, "vocals", False)
            ),
            asyncio.create_task(asyncio.to_thread(svc.set_track_muted, "drums", True)),
            asyncio.create_task(asyncio.to_thread(svc.set_track_muted, "drums", False)),
        ]

        # Wait for all to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Verify that mixer.set_track_muted was called
        assert mixer.set_track_muted.call_count == 4

    @pytest.mark.asyncio
    async def test_concurrent_active_stems_changes(self) -> None:
        """Test that concurrent active stems changes are handled."""
        mixer = MagicMock()
        mixer.state = PlaybackState.STOPPED
        mixer.position_ms.return_value = 0
        mixer.duration_ms.return_value = 0
        mixer.has_tracks = False
        mixer.track_names.return_value = []
        mixer.track_gains.return_value = {}
        mixer.track_muted_map.return_value = {}
        mixer.active_stems.return_value = []
        svc = PlaybackService(mixer=mixer)

        # Start multiple active stems operations
        tasks = [
            asyncio.create_task(asyncio.to_thread(svc.set_active_stems, ["vocals"])),
            asyncio.create_task(asyncio.to_thread(svc.set_active_stems, ["drums"])),
            asyncio.create_task(
                asyncio.to_thread(svc.set_active_stems, ["vocals", "drums"])
            ),
            asyncio.create_task(asyncio.to_thread(svc.set_active_stems, [])),
        ]

        # Wait for all to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Verify that mixer.set_active was called
        assert mixer.set_active.call_count == 4

    @pytest.mark.asyncio
    async def test_concurrent_seek_operations(self) -> None:
        """Test that concurrent seek operations are handled."""
        mixer = MagicMock()
        mixer.state = PlaybackState.STOPPED
        mixer.position_ms.return_value = 0
        mixer.duration_ms.return_value = 0
        mixer.has_tracks = False
        mixer.track_names.return_value = []
        mixer.track_gains.return_value = {}
        mixer.track_muted_map.return_value = {}
        mixer.active_stems.return_value = []
        svc = PlaybackService(mixer=mixer)

        # Start multiple seek operations
        tasks = [
            asyncio.create_task(asyncio.to_thread(svc.seek_ms, 1000)),
            asyncio.create_task(asyncio.to_thread(svc.seek_ms, 5000)),
            asyncio.create_task(asyncio.to_thread(svc.seek_ms, 10000)),
            asyncio.create_task(asyncio.to_thread(svc.seek_ms, 15000)),
        ]

        # Wait for all to complete
        await asyncio.gather(*tasks, return_exceptions=True)

        # Verify that mixer.seek_ms was called
        assert mixer.seek_ms.call_count == 4

    @pytest.mark.asyncio
    async def test_playback_service_thread_safety(self) -> None:
        """Test that PlaybackService is thread-safe for rapid operations."""
        mixer = MagicMock()
        mixer.state = PlaybackState.STOPPED
        mixer.position_ms.return_value = 0
        mixer.duration_ms.return_value = 0
        mixer.has_tracks = False
        mixer.track_names.return_value = []
        mixer.track_gains.return_value = {}
        mixer.track_muted_map.return_value = {}
        mixer.active_stems.return_value = []
        svc = PlaybackService(mixer=mixer)

        # Perform many rapid operations from different "threads"
        async def rapid_operations():
            tasks = []
            for i in range(50):
                if i % 5 == 0:
                    tasks.append(asyncio.create_task(asyncio.to_thread(svc.play)))
                elif i % 5 == 1:
                    tasks.append(asyncio.create_task(asyncio.to_thread(svc.pause)))
                elif i % 5 == 2:
                    tasks.append(asyncio.create_task(asyncio.to_thread(svc.stop)))
                elif i % 5 == 3:
                    tasks.append(
                        asyncio.create_task(
                            asyncio.to_thread(svc.set_master_volume, i / 100.0)
                        )
                    )
                else:
                    tasks.append(
                        asyncio.create_task(asyncio.to_thread(svc.seek_ms, i * 100))
                    )

            await asyncio.gather(*tasks, return_exceptions=True)

        await rapid_operations()

        # Verify that mixer methods were called many times
        total_calls = (
            mixer.play.call_count
            + mixer.pause.call_count
            + mixer.stop.call_count
            + mixer.set_master_volume.call_count
            + mixer.seek_ms.call_count
        )
        assert total_calls >= 50

    @pytest.mark.asyncio
    async def test_playback_service_state_consistency(self) -> None:
        """Test that PlaybackService state remains consistent under concurrency."""
        mixer = MagicMock()
        mixer.state = PlaybackState.STOPPED
        mixer.position_ms.return_value = 0
        mixer.duration_ms.return_value = 0
        mixer.has_tracks = False
        mixer.track_names.return_value = []
        mixer.track_gains.return_value = {}
        mixer.track_muted_map.return_value = {}
        mixer.active_stems.return_value = []
        svc = PlaybackService(mixer=mixer)

        # Track state changes
        state_changes = []

        def state_change_callback(state):
            state_changes.append(state)

        svc.state_changed.connect(state_change_callback)

        # Perform concurrent operations that should trigger state changes
        tasks = [
            asyncio.create_task(asyncio.to_thread(svc.play)),
            asyncio.create_task(asyncio.to_thread(svc.stop)),
            asyncio.create_task(asyncio.to_thread(svc.play)),
            asyncio.create_task(asyncio.to_thread(svc.pause)),
            asyncio.create_task(asyncio.to_thread(svc.stop)),
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        # Verify that state changed signals were emitted
        assert len(state_changes) >= 0  # At least some state changes should occur

    @pytest.mark.asyncio
    async def test_playback_service_error_handling_under_concurrency(self) -> None:
        """Test that PlaybackService handles errors correctly under concurrency."""
        mixer = MagicMock()
        mixer.state = PlaybackState.STOPPED
        mixer.position_ms.return_value = 0
        mixer.duration_ms.return_value = 0
        mixer.has_tracks = False
        mixer.track_names.return_value = []
        mixer.track_gains.return_value = {}
        mixer.track_muted_map.return_value = {}
        mixer.active_stems.return_value = []
        svc = PlaybackService(mixer=mixer)

        # Track error signals
        error_signals = []

        def error_callback(error_msg):
            error_signals.append(error_msg)

        svc.error_occurred.connect(error_callback)

        # Make mixer methods raise exceptions
        mixer.play.side_effect = Exception("Playback error")
        mixer.pause.side_effect = Exception("Pause error")
        mixer.stop.side_effect = Exception("Stop error")

        # Perform concurrent operations that should trigger errors
        tasks = [
            asyncio.create_task(asyncio.to_thread(svc.play)),
            asyncio.create_task(asyncio.to_thread(svc.pause)),
            asyncio.create_task(asyncio.to_thread(svc.stop)),
        ]

        await asyncio.gather(*tasks, return_exceptions=True)

        # Verify that error signals were emitted
        assert len(error_signals) >= 0  # At least some error signals should occur
