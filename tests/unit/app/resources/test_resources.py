"""Tests for app.resources package."""

import app.resources as resources


def test_resources_package_exists() -> None:
    """Test that the resources package can be imported."""
    assert resources is not None


def test_resources_all_is_empty() -> None:
    """Test that __all__ is an empty list."""
    assert resources.__all__ == []


def test_resources_has_docstring() -> None:
    """Test that the resources package has a docstring."""
    assert resources.__doc__ is not None
    assert "Icons, translations, static assets" in resources.__doc__
