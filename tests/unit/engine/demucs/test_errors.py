"""Unit tests for engine.demucs.errors."""

import pytest

from engine.demucs.errors import (
    InferenceError,
    InvalidAudioError,
    ModelLoadError,
    ProcessingError,
    SeparationError,
)


class TestSeparationError:
    def test_base_message(self) -> None:
        err = SeparationError()
        assert str(err) == "Separation operation failed"

    def test_custom_message(self) -> None:
        err = SeparationError("custom")
        assert str(err) == "custom"

    def test_is_exception(self) -> None:
        assert issubclass(SeparationError, Exception)


class TestModelLoadError:
    def test_default_message(self) -> None:
        err = ModelLoadError()
        assert str(err) == "Model loading failed"

    def test_custom_message(self) -> None:
        err = ModelLoadError("model not found")
        assert str(err) == "model not found"

    def test_is_separation_error(self) -> None:
        assert issubclass(ModelLoadError, SeparationError)


class TestInferenceError:
    def test_default_message(self) -> None:
        err = InferenceError()
        assert str(err) == "Inference operation failed"

    def test_custom_message(self) -> None:
        err = InferenceError("inference failed")
        assert str(err) == "inference failed"

    def test_is_separation_error(self) -> None:
        assert issubclass(InferenceError, SeparationError)

    def test_catchable_as_separation_error(self) -> None:
        with pytest.raises(SeparationError):
            raise InferenceError("test")


class TestProcessingError:
    def test_default_message(self) -> None:
        err = ProcessingError()
        assert str(err) == "Audio processing failed"

    def test_custom_message(self) -> None:
        err = ProcessingError("processing error")
        assert str(err) == "processing error"

    def test_is_separation_error(self) -> None:
        assert issubclass(ProcessingError, SeparationError)


class TestInvalidAudioError:
    def test_default_message(self) -> None:
        err = InvalidAudioError()
        assert str(err) == "Invalid audio input"

    def test_custom_message(self) -> None:
        err = InvalidAudioError("invalid format")
        assert str(err) == "invalid format"

    def test_is_separation_error(self) -> None:
        assert issubclass(InvalidAudioError, SeparationError)
