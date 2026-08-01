"""Tests for ResourceMonitor (psutil async sampling)."""

from __future__ import annotations

import asyncio
from unittest.mock import MagicMock

import pytest

from engine.performance.monitor import ResourceMonitor, ResourceSnapshot


@pytest.fixture
def fake_process() -> MagicMock:
    """Fake psutil.Process with controllable memory/cpu."""
    process = MagicMock()
    process.cpu_percent.return_value = 12.5
    info = MagicMock()
    info.rss = 1_000_000
    info.vms = 2_000_000
    process.memory_info.return_value = info
    return process


@pytest.fixture
def fake_swap() -> MagicMock:
    """Fake psutil.swap_memory module-level call."""
    swap = MagicMock()
    swap.total = 8_000_000_000
    swap.free = 4_000_000_000
    return swap


async def test_snapshot_model_fields() -> None:
    """ResourceSnapshot stores the sampled values."""
    snap = ResourceSnapshot(
        timestamp=1.0, cpu_percent=5.0, rss_bytes=100, vms_bytes=200, swap_bytes=300
    )
    assert snap.cpu_percent == 5.0
    assert snap.rss_bytes == 100
    assert snap.swap_bytes == 300


async def test_start_primes_cpu_percent(
    monkeypatch: pytest.MonkeyPatch, fake_process: MagicMock
) -> None:
    """start() must call cpu_percent once before sampling (prime)."""
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.Process", lambda: fake_process
    )
    monitor = ResourceMonitor()
    await monitor.start()
    # Prime call + each sample call.
    assert fake_process.cpu_percent.call_count >= 1
    assert monitor.running


async def test_start_stop_idempotent(
    monkeypatch: pytest.MonkeyPatch, fake_process: MagicMock
) -> None:
    """Repeated start/stop should not raise or double-prime."""
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.Process", lambda: fake_process
    )
    monitor = ResourceMonitor()
    await monitor.start()
    await monitor.start()
    await monitor.stop()
    await monitor.stop()
    assert not monitor.running


async def test_sample_reports_values(
    monkeypatch: pytest.MonkeyPatch,
    fake_process: MagicMock,
    fake_swap: MagicMock,
) -> None:
    """sample() returns correct values and tracks peak RSS."""
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.Process", lambda: fake_process
    )
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.swap_memory", lambda: fake_swap
    )

    monitor = ResourceMonitor()
    snap = await monitor.sample()

    assert snap.cpu_percent == 12.5
    assert snap.rss_bytes == 1_000_000
    assert snap.vms_bytes == 2_000_000
    assert snap.swap_bytes == 4_000_000_000
    assert monitor.peak_rss_bytes == 1_000_000
    assert monitor.sample_count == 1


async def test_peak_rss_tracks_maximum(
    monkeypatch: pytest.MonkeyPatch, fake_process: MagicMock, fake_swap: MagicMock
) -> None:
    """Peak RSS is the max over all samples."""
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.Process", lambda: fake_process
    )
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.swap_memory", lambda: fake_swap
    )
    info = MagicMock()
    info.rss = 2_500_000
    info.vms = 2_000_000
    fake_process.memory_info.side_effect = [info, info]

    monitor = ResourceMonitor()
    await monitor.sample()
    await monitor.sample()
    assert monitor.peak_rss_bytes == 2_500_000


async def test_callback_invoked(
    monkeypatch: pytest.MonkeyPatch,
    fake_process: MagicMock,
    fake_swap: MagicMock,
) -> None:
    """The async callback receives each snapshot."""
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.Process", lambda: fake_process
    )
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.swap_memory", lambda: fake_swap
    )
    received: list[ResourceSnapshot] = []

    async def cb(snap: ResourceSnapshot) -> None:
        received.append(snap)

    monitor = ResourceMonitor(callback=cb)
    await monitor.sample()
    assert len(received) == 1
    assert received[0].rss_bytes == 1_000_000


async def test_stop_takes_final_sample(
    monkeypatch: pytest.MonkeyPatch, fake_process: MagicMock
) -> None:
    """stop() samples once more before marking not-running."""
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.Process", lambda: fake_process
    )
    monitor = ResourceMonitor()
    await monitor.start()
    await monitor.stop()
    assert monitor.sample_count == 1


def test_summary_format(
    monkeypatch: pytest.MonkeyPatch, fake_process: MagicMock, fake_swap: MagicMock
) -> None:
    """summary() produces a compact loguru-friendly string."""
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.Process", lambda: fake_process
    )
    monkeypatch.setattr(
        "engine.performance.monitor.psutil.swap_memory", lambda: fake_swap
    )
    monitor = ResourceMonitor(interval=0.5)
    asyncio.run(monitor.sample())
    summary = monitor.summary()
    assert "peak RSS=" in summary
    assert "1.0 MB" in summary
    assert "samples=1" in summary
