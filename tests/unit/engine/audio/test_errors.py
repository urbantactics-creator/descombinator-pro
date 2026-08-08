"""Unit tests for engine.audio.errors — exception hierarchy."""

import pytest

from engine.audio.errors import (
    AudioError,
    AudioFileNotFoundError,
    AudioFormatError,
    AudioLoadError,
    MetadataError,
    PostprocessingError,
    PreprocessingError,
    ResampleError,
)


class TestAudioError:
    def test_base_message(self) -> None:
        err = AudioError()
        assert str(err) == ""

    def test_custom_message(self) -> None:
        err = AudioError("custom")
        assert str(err) == "custom"

    def test_is_exception(self) -> None:
        assert issubclass(AudioError, Exception)


ALL_SUBCLASSES = [
    AudioLoadError,
    AudioFormatError,
    ResampleError,
    PreprocessingError,
    PostprocessingError,
    MetadataError,
    AudioFileNotFoundError,
]


class TestAudioErrorSubclasses:
    @pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
    def test_is_audio_error(self, exc_cls: type) -> None:
        assert issubclass(exc_cls, AudioError)

    @pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
    def test_custom_message(self, exc_cls: type) -> None:
        err = exc_cls("test msg")
        assert str(err) == "test msg"

    @pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
    def test_catchable_as_audio_error(self, exc_cls: type) -> None:
        with pytest.raises(AudioError):
            raise exc_cls("test")

    @pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
    def test_catchable_as_exception(self, exc_cls: type) -> None:
        with pytest.raises(AudioError):
            raise exc_cls("test")


class TestAudioLoadError:
    def test_default_message(self) -> None:
        err = AudioLoadError()
        assert str(err) == ""


class TestAudioFormatError:
    def test_default_message(self) -> None:
        err = AudioFormatError()
        assert str(err) == ""


class TestAudioFileNotFoundError:
    def test_default_message(self) -> None:
        err = AudioFileNotFoundError()
        assert str(err) == ""
