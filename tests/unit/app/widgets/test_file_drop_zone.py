"""Unit tests for app.widgets.file_drop_zone — FileDropZone."""

from app.widgets.file_drop_zone import FileDropZone


class TestFileDropZoneSupportedFormats:
    """Tests for SUPPORTED_FORMATS constant."""

    def test_contains_expected_extensions(self) -> None:
        assert ".wav" in FileDropZone.SUPPORTED_FORMATS
        assert ".mp3" in FileDropZone.SUPPORTED_FORMATS
        assert ".flac" in FileDropZone.SUPPORTED_FORMATS
        assert ".m4a" in FileDropZone.SUPPORTED_FORMATS
        assert ".ogg" in FileDropZone.SUPPORTED_FORMATS
        assert ".aiff" in FileDropZone.SUPPORTED_FORMATS


class TestFileDropZoneIsSupported:
    """Tests for _is_supported private method."""

    def test_wav_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.wav") is True

    def test_mp3_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.mp3") is True

    def test_flac_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.flac") is True

    def test_m4a_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.m4a") is True

    def test_ogg_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.ogg") is True

    def test_aiff_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.aiff") is True

    def test_txt_not_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.txt") is False

    def test_exe_not_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.exe") is False

    def test_pdf_not_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.pdf") is False

    def test_no_extension_not_supported(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file") is False

    def test_case_insensitive(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert zone._is_supported("/path/to/file.WAV") is True
        assert zone._is_supported("/path/to/file.Mp3") is True
        assert zone._is_supported("/path/to/file.FLAC") is True


class TestFileDropZoneSetMessage:
    """Tests for set_message method."""

    def test_set_message_updates_label(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        zone.set_message("New message")
        assert zone._label.text() == "New message"

    def test_set_message_empty_string(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        zone.set_message("")
        assert zone._label.text() == ""


class TestFileDropZoneSignal:
    """Tests for file_dropped signal."""

    def test_signal_exists(self, qapp) -> None:  # type: ignore[no-untyped-def]
        zone = FileDropZone()
        assert hasattr(zone, "file_dropped")
