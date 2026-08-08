"""Unit tests for engine.inference.errors — exception hierarchy."""

import pytest

from engine.inference.errors import (
    DeviceError,
    InferenceError,
    InferenceTimeoutError,
    ModelLoadError,
    ModelNotFoundError,
)


class TestInferenceError:
    def test_base_message(self) -> None:
        err = InferenceError()
        assert str(err) == ""

    def test_custom_message(self) -> None:
        err = InferenceError("custom")
        assert str(err) == "custom"

    def test_is_exception(self) -> None:
        assert issubclass(InferenceError, Exception)


class TestModelLoadErrorInference:
    def test_is_inference_error(self) -> None:
        assert issubclass(ModelLoadError, InferenceError)

    def test_custom_message(self) -> None:
        err = ModelLoadError("load failed")
        assert str(err) == "load failed"


class TestModelNotFoundError:
    def test_is_inference_error(self) -> None:
        assert issubclass(ModelNotFoundError, InferenceError)

    def test_custom_message(self) -> None:
        err = ModelNotFoundError("not found")
        assert str(err) == "not found"


class TestInferenceTimeoutError:
    def test_is_inference_error(self) -> None:
        assert issubclass(InferenceTimeoutError, InferenceError)

    def test_custom_message(self) -> None:
        err = InferenceTimeoutError("timed out")
        assert str(err) == "timed out"


class TestDeviceError:
    def test_is_inference_error(self) -> None:
        assert issubclass(DeviceError, InferenceError)

    def test_custom_message(self) -> None:
        err = DeviceError("no GPU")
        assert str(err) == "no GPU"


class TestInferenceHierarchy:
    def test_catch_all_as_inference_error(self) -> None:
        exc_list = [
            ModelLoadError,
            ModelNotFoundError,
            InferenceTimeoutError,
            DeviceError,
        ]
        for exc_cls in exc_list:
            with pytest.raises(InferenceError):
                raise exc_cls("test")

    def test_catch_all_as_exception(self) -> None:
        exc_list = [
            InferenceError,
            ModelLoadError,
            ModelNotFoundError,
            InferenceTimeoutError,
            DeviceError,
        ]
        for exc_cls in exc_list:
            with pytest.raises(InferenceError):
                raise exc_cls("test")
