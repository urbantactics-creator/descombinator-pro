"""Unit tests for engine.export.errors — exception hierarchy."""

from __future__ import annotations

import pytest

from engine.export.errors import (
    ExportError,
    MetadataError,
    UnsupportedFormatError,
    WriteError,
)


class TestExportError:
    def test_base_message(self) -> None:
        err = ExportError()
        assert str(err) == ""

    def test_custom_message(self) -> None:
        err = ExportError("custom")
        assert str(err) == "custom"

    def test_is_exception(self) -> None:
        assert issubclass(ExportError, Exception)


ALL_SUBCLASSES = [UnsupportedFormatError, WriteError, MetadataError]


class TestExportErrorSubclasses:
    @pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
    def test_is_export_error(self, exc_cls: type) -> None:
        assert issubclass(exc_cls, ExportError)

    @pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
    def test_custom_message(self, exc_cls: type) -> None:
        err = exc_cls("test msg")
        assert str(err) == "test msg"

    @pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
    def test_catchable_as_export_error(self, exc_cls: type) -> None:
        with pytest.raises(ExportError):
            raise exc_cls("test")

    @pytest.mark.parametrize("exc_cls", ALL_SUBCLASSES)
    def test_catchable_as_exception(self, exc_cls: type) -> None:
        with pytest.raises(ExportError):
            raise exc_cls("test")
