"""Shared test fixtures and markers."""

import pathlib

import pytest


@pytest.fixture
def sample_audio_path() -> pathlib.Path:
    """Return path to sample test audio file."""
    return pathlib.Path("tests/fixtures/sample.wav")


@pytest.fixture
def tmp_output_dir(tmp_path: pathlib.Path) -> pathlib.Path:
    """Return a temporary output directory."""
    output_dir = tmp_path / "output"
    output_dir.mkdir()
    return output_dir
