"""Unit tests for app.widgets.track_selector — TrackSelector."""

from __future__ import annotations

from app.widgets.track_selector import TrackSelector


class TestTrackSelectorDefaults:
    """Tests for TrackSelector defaults."""

    def test_default_stems(self) -> None:
        assert TrackSelector.DEFAULT_STEMS == ["vocals", "drums", "bass", "other"]

    def test_creates_without_error(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        assert selector is not None

    def test_creates_four_checkboxes(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        assert len(selector._checkboxes) == 4

    def test_checkbox_keys_match_stems(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        assert set(selector._checkboxes.keys()) == {
            "vocals",
            "drums",
            "bass",
            "other",
        }

    def test_default_selection_vocals_and_other(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        assert "vocals" in selector.selected_stems
        assert "other" in selector.selected_stems
        assert "drums" not in selector.selected_stems
        assert "bass" not in selector.selected_stems


class TestTrackSelectorSelectedStems:
    """Tests for selected_stems property."""

    def test_selected_stems_returns_list(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        result = selector.selected_stems
        assert isinstance(result, list)

    def test_selected_stems_default_length(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        assert len(selector.selected_stems) == 2


class TestTrackSelectorSetSelectedStems:
    """Tests for set_selected_stems method."""

    def test_set_selected_stems_updates_checkboxes(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        selector.set_selected_stems(["drums"])
        assert selector.selected_stems == ["drums"]

    def test_set_selected_stems_multiple(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        selector.set_selected_stems(["drums", "bass"])
        selected = selector.selected_stems
        assert "drums" in selected
        assert "bass" in selected
        assert "vocals" not in selected
        assert "other" not in selected

    def test_set_selected_stems_empty(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        selector.set_selected_stems([])
        assert selector.selected_stems == []


class TestTrackSelectorClearSelection:
    """Tests for clear_selection method."""

    def test_clear_selection_unchecks_all(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        selector.clear_selection()
        assert selector.selected_stems == []


class TestTrackSelectorSignal:
    """Tests for stems_changed signal."""

    def test_signal_exists(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        assert hasattr(selector, "stems_changed")

    def test_signal_emitted_on_set_selected_stems(self, qapp) -> None:  # type: ignore[no-untyped-def]
        selector = TrackSelector()
        emitted = []
        selector.stems_changed.connect(lambda stems: emitted.append(stems))
        selector.set_selected_stems(["bass"])
        assert len(emitted) >= 1
        assert "bass" in emitted[-1]
