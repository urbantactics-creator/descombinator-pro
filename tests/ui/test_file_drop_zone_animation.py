"""Tests for the FileDropZone animation features."""

from PySide6.QtCore import QAbstractAnimation, QEasingCurve

from app.widgets.file_drop_zone import FileDropZone


def _stop_anims(widget):
    widget._enter_anim.stop()
    widget._exit_anim.stop()
    widget._opacity_anim.stop()


def test_enter_anim_configured(qapp):
    widget = FileDropZone()
    try:
        assert widget._enter_anim.duration() == 200
        assert widget._enter_anim.easingCurve().type() == QEasingCurve.OutCubic
        assert widget._enter_anim.targetObject() is widget._label
        assert widget._enter_anim.propertyName() == b"styleSheet"
    finally:
        _stop_anims(widget)


def test_exit_anim_configured(qapp):
    widget = FileDropZone()
    try:
        assert widget._exit_anim.duration() == 150
        assert widget._exit_anim.easingCurve().type() == QEasingCurve.InCubic
        assert widget._exit_anim.targetObject() is widget._label
        assert widget._exit_anim.propertyName() == b"styleSheet"
    finally:
        _stop_anims(widget)


def test_opacity_anim_configured(qapp):
    widget = FileDropZone()
    try:
        assert widget._opacity_anim.duration() == 200
        assert widget._opacity_anim.targetObject() is widget._opacity_effect
        assert widget._opacity_anim.propertyName() == b"opacity"
    finally:
        _stop_anims(widget)


def test_apply_drag_style_enter_valid(qapp):
    widget = FileDropZone()
    try:
        widget._apply_drag_style(True, valid=True)
        assert widget._label.text() == "Drop to load audio file"
        assert "#4CAF50" in widget._enter_anim.endValue()
        assert widget._enter_anim.state() == QAbstractAnimation.Running
    finally:
        _stop_anims(widget)


def test_apply_drag_style_enter_invalid(qapp):
    widget = FileDropZone()
    try:
        widget._apply_drag_style(True, valid=False)
        assert widget._label.text() == "Unsupported format"
        assert "#f44336" in widget._enter_anim.endValue()
    finally:
        _stop_anims(widget)


def test_apply_drag_style_leave(qapp):
    widget = FileDropZone()
    try:
        widget._apply_drag_style(False)
        assert widget._label.text() == "Drag & drop an audio file here"
        assert "#888" in widget._exit_anim.endValue()
        assert "dashed" in widget._exit_anim.endValue()
        assert widget._exit_anim.state() == QAbstractAnimation.Running
    finally:
        _stop_anims(widget)


def test_opacity_anim_reset_to_one(qapp):
    widget = FileDropZone()
    try:
        widget._apply_drag_style(True)
        assert widget._opacity_anim.endValue() == 1.0
    finally:
        _stop_anims(widget)
