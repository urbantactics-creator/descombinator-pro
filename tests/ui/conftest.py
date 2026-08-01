"""Shared test fixtures for UI tests."""

import sys

import pytest
from PySide6.QtWidgets import QApplication


@pytest.fixture(scope="session")
def qapp():
    """Create a QApplication instance for tests."""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app
    # Don't quit the app here as it might be used in other tests


@pytest.fixture
def temp_wav_file(tmp_path):
    """Create a temporary WAV file for testing."""
    wav_file = tmp_path / "test.wav"
    # Write a minimal WAV header + some data
    # This is a very basic WAV file for testing purposes
    wav_data = (
        b"RIFF\x24\x00\x00\x00"  # ChunkID + ChunkSize (36 bytes)
        b"WAVE"  # Format
        b"fmt \x10\x00\x00\x00"  # Subchunk1ID + Subchunk1Size (16)
        b"\x01\x00"  # AudioFormat (PCM)
        b"\x01\x00"  # NumChannels (1)
        b"\x44\xac\x00\x00"  # SampleRate (44100)
        b"\x88\x58\x01\x00"  # ByteRate (SampleRate * NumChannels * BitsPerSample/8)
        b"\x02\x00"  # BlockAlign (NumChannels * BitsPerSample/8)
        b"\x10\x00"  # BitsPerSample (16)
        b"data\x00\x00\x00\x00"  # Subchunk2ID + Subchunk2Size (0 data bytes)
    )
    wav_file.write_bytes(wav_data)
    return wav_file
