"""Tests for app.resources package."""

from __future__ import annotations

import app.resources as resources


def test_resources_package_exists():
    """Test that the resources package can be imported."""
    assert resources is not None


def test_resources_all_is_empty():
    """Test that __all__ is an empty list."""
    assert resources.__all__ == []


def test_resources_has_docstring():
    """Test that the resources package has a docstring."""
    assert resources.__doc__ is not None
    assert "Icons, translations, static assets" in resources.__doc__
