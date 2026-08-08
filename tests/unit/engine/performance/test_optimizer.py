"""Tests for TorchRuntimeOptimizer CPU/GPU runtime configuration."""

from unittest.mock import MagicMock

import pytest

from engine.performance.optimizer import TorchRuntimeOptimizer


@pytest.fixture(autouse=True)
def reset_optimizer() -> None:
    """Reset the once-per-process flag between tests."""
    TorchRuntimeOptimizer._configured = False
    yield
    TorchRuntimeOptimizer._configured = False


def test_configure_sets_threads_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without jobs, threads follow MAX_WORKERS (fallback to cpu_count)."""
    fake_torch = MagicMock()
    fake_torch.backends.mkldnn = MagicMock()
    fake_torch.backends.mkldnn.is_available.return_value = False
    monkeypatch.setenv("MAX_WORKERS", "4")
    monkeypatch.setattr("engine.performance.optimizer.torch", fake_torch, raising=False)
    monkeypatch.setitem(__import__("sys").modules, "torch", fake_torch)

    TorchRuntimeOptimizer.configure()
    assert fake_torch.set_num_threads.call_args_list[0] == ((4,),)


def test_configure_jobs_over_one_uses_single_thread(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """jobs > 1 restricts each process worker to a single thread."""
    fake_torch = MagicMock()
    fake_torch.backends.mkldnn = MagicMock()
    monkeypatch.setitem(__import__("sys").modules, "torch", fake_torch)

    TorchRuntimeOptimizer.configure(jobs=4)
    assert fake_torch.set_num_threads.call_args_list[0] == ((1,),)


def test_configure_fallback_cpu_count(monkeypatch: pytest.MonkeyPatch) -> None:
    """Without MAX_WORKERS, falls back to os.cpu_count()."""
    fake_torch = MagicMock()
    fake_torch.backends.mkldnn = MagicMock()
    monkeypatch.delenv("MAX_WORKERS", raising=False)
    monkeypatch.setattr("os.cpu_count", lambda: 8)
    monkeypatch.setitem(__import__("sys").modules, "torch", fake_torch)

    TorchRuntimeOptimizer.configure()
    assert fake_torch.set_num_threads.call_args_list[0] == ((8,),)


def test_configure_enables_mkldnn(monkeypatch: pytest.MonkeyPatch) -> None:
    """mkldnn is enabled when available."""
    fake_torch = MagicMock()
    fake_torch.backends.mkldnn = MagicMock()
    fake_torch.backends.mkldnn.is_available.return_value = True
    monkeypatch.setitem(__import__("sys").modules, "torch", fake_torch)

    TorchRuntimeOptimizer.configure()
    assert fake_torch.backends.mkldnn.enabled is True


def test_configure_skips_missing_mkldnn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Missing mkldnn backend does not raise."""
    fake_torch = MagicMock()
    del fake_torch.backends.mkldnn
    monkeypatch.setitem(__import__("sys").modules, "torch", fake_torch)

    TorchRuntimeOptimizer.configure()
    # No assertion needed beyond not raising.


def test_configure_idempotent(monkeypatch: pytest.MonkeyPatch) -> None:
    """Calling configure twice only configures once."""
    fake_torch = MagicMock()
    fake_torch.backends.mkldnn = MagicMock()
    monkeypatch.setitem(__import__("sys").modules, "torch", fake_torch)

    TorchRuntimeOptimizer.configure()
    TorchRuntimeOptimizer.configure(jobs=2)
    assert fake_torch.set_num_threads.call_count == 1


def test_autocast_ctx_enabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """autocast_ctx passes enabled=True when mixed precision requested."""
    entered: list[bool] = []

    class _FakeAutocast:
        def __init__(self, device_type: str, enabled: bool) -> None:
            entered.append(enabled)

        def __enter__(self) -> None:
            pass

        def __exit__(self, *args: object) -> None:
            pass

    fake_torch = MagicMock()
    fake_torch.autocast = MagicMock(return_value=_FakeAutocast("cuda", True))
    monkeypatch.setitem(__import__("sys").modules, "torch", fake_torch)

    with TorchRuntimeOptimizer.autocast_ctx(True, "cuda"):
        pass
    assert entered == [True]


def test_autocast_ctx_disabled(monkeypatch: pytest.MonkeyPatch) -> None:
    """autocast_ctx passes enabled=False without mixed precision."""
    entered: list[bool] = []

    class _FakeAutocast:
        def __init__(self, device_type: str, enabled: bool) -> None:
            entered.append(enabled)

        def __enter__(self) -> None:
            pass

        def __exit__(self, *args: object) -> None:
            pass

    fake_torch = MagicMock()
    fake_torch.autocast = MagicMock(return_value=_FakeAutocast("cuda", False))
    monkeypatch.setitem(__import__("sys").modules, "torch", fake_torch)

    with TorchRuntimeOptimizer.autocast_ctx(False, "cuda"):
        pass
    assert entered == [False]
