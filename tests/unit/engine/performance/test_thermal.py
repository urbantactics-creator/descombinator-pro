"""Unit tests for engine.performance.thermal — ThermalMonitor, ThermalState."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from engine.performance.thermal import ThermalMonitor, ThermalSnapshot, ThermalState


class TestThermalState:
    def test_enum_values(self) -> None:
        assert ThermalState.NORMAL == "normal"
        assert ThermalState.WARM == "warm"
        assert ThermalState.HOT == "hot"
        assert ThermalState.CRITICAL == "critical"

    def test_count(self) -> None:
        assert len(ThermalState) == 4

    def test_ordering(self) -> None:
        states = list(ThermalState)
        assert states == [
            ThermalState.NORMAL,
            ThermalState.WARM,
            ThermalState.HOT,
            ThermalState.CRITICAL,
        ]


class TestThermalSnapshot:
    def test_defaults(self) -> None:
        snap = ThermalSnapshot()
        assert snap.cpu_temp_c is None
        assert snap.gpu_temp_c is None
        assert snap.state == ThermalState.NORMAL

    def test_with_temps(self) -> None:
        snap = ThermalSnapshot(
            cpu_temp_c=65.0, gpu_temp_c=72.0, state=ThermalState.WARM
        )
        assert snap.cpu_temp_c == 65.0
        assert snap.gpu_temp_c == 72.0
        assert snap.state == ThermalState.WARM


class TestThermalMonitorEvaluate:
    def test_both_none_returns_normal(self) -> None:
        assert ThermalMonitor._evaluate(None, None) == ThermalState.NORMAL

    def test_cpu_normal(self) -> None:
        assert ThermalMonitor._evaluate(50.0, None) == ThermalState.NORMAL

    def test_cpu_warm(self) -> None:
        assert ThermalMonitor._evaluate(75.0, None) == ThermalState.WARM

    def test_cpu_hot(self) -> None:
        assert ThermalMonitor._evaluate(85.0, None) == ThermalState.HOT

    def test_cpu_critical(self) -> None:
        assert ThermalMonitor._evaluate(95.0, None) == ThermalState.CRITICAL

    def test_gpu_normal(self) -> None:
        assert ThermalMonitor._evaluate(None, 60.0) == ThermalState.NORMAL

    def test_gpu_warm(self) -> None:
        assert ThermalMonitor._evaluate(None, 82.0) == ThermalState.WARM

    def test_gpu_hot(self) -> None:
        assert ThermalMonitor._evaluate(None, 90.0) == ThermalState.HOT

    def test_gpu_critical(self) -> None:
        assert ThermalMonitor._evaluate(None, 100.0) == ThermalState.CRITICAL

    def test_cpu_warm_gpu_hot_returns_hot(self) -> None:
        result = ThermalMonitor._evaluate(75.0, 90.0)
        assert result == ThermalState.HOT

    def test_cpu_hot_gpu_warm_returns_hot(self) -> None:
        result = ThermalMonitor._evaluate(85.0, 82.0)
        assert result == ThermalState.HOT

    def test_cpu_normal_gpu_critical_returns_critical(self) -> None:
        assert ThermalMonitor._evaluate(50.0, 100.0) == ThermalState.CRITICAL

    def test_cpu_critical_gpu_normal_returns_critical(self) -> None:
        assert ThermalMonitor._evaluate(95.0, 50.0) == ThermalState.CRITICAL

    def test_boundary_cpu_warm(self) -> None:
        assert ThermalMonitor._evaluate(70.0, None) == ThermalState.WARM

    def test_boundary_cpu_hot(self) -> None:
        assert ThermalMonitor._evaluate(80.0, None) == ThermalState.HOT

    def test_boundary_cpu_critical(self) -> None:
        assert ThermalMonitor._evaluate(90.0, None) == ThermalState.CRITICAL


class TestThermalMonitorInit:
    def test_initial_state(self) -> None:
        mon = ThermalMonitor()
        assert mon.state == ThermalState.NORMAL


class TestThermalMonitorReadCpuTemp:
    @pytest.mark.asyncio
    async def test_linux_coretemp(self) -> None:
        import psutil

        fake_shw = MagicMock()
        fake_shw.current = 65.0
        with patch.object(
            psutil, "sensors_temperatures", return_value={"coretemp": [fake_shw]}
        ):
            result = await ThermalMonitor._read_cpu_temp()
            assert result == 65.0

    @pytest.mark.asyncio
    async def test_linux_k10temp(self) -> None:
        import psutil

        fake_shw = MagicMock()
        fake_shw.current = 55.0
        with patch.object(
            psutil, "sensors_temperatures", return_value={"k10temp": [fake_shw]}
        ):
            result = await ThermalMonitor._read_cpu_temp()
            assert result == 55.0

    @pytest.mark.asyncio
    async def test_no_sensors_returns_none(self) -> None:
        import psutil

        with patch.object(psutil, "sensors_temperatures", return_value={}):
            result = await ThermalMonitor._read_cpu_temp()
            assert result is None

    @pytest.mark.asyncio
    async def test_psutil_not_available(self) -> None:
        with patch.dict("sys.modules", {"psutil": None}):
            result = await ThermalMonitor._read_cpu_temp()
            assert result is None

    @pytest.mark.asyncio
    async def test_first_key_fallback(self) -> None:
        import psutil

        fake_shw = MagicMock()
        fake_shw.current = 72.0
        with patch.object(
            psutil, "sensors_temperatures", return_value={"unknown_sensor": [fake_shw]}
        ):
            result = await ThermalMonitor._read_cpu_temp()
            assert result == 72.0


class TestThermalMonitorReadGpuTemp:
    @pytest.mark.asyncio
    async def test_nvidia_smi_success(self) -> None:
        mock_proc = MagicMock()
        mock_proc.returncode = 0
        mock_proc.stdout = "75\n"
        with patch("engine.performance.thermal.subprocess.run", return_value=mock_proc):
            result = await ThermalMonitor._read_gpu_temp()
            assert result == 75.0

    @pytest.mark.asyncio
    async def test_nvidia_smi_not_found(self) -> None:
        with patch(
            "engine.performance.thermal.subprocess.run",
            side_effect=FileNotFoundError,
        ):
            result = await ThermalMonitor._read_gpu_temp()
            assert result is None

    @pytest.mark.asyncio
    async def test_nvidia_smi_timeout(self) -> None:
        import subprocess

        with patch(
            "engine.performance.thermal.subprocess.run",
            side_effect=subprocess.TimeoutExpired("nvidia-smi", 5),
        ):
            result = await ThermalMonitor._read_gpu_temp()
            assert result is None

    @pytest.mark.asyncio
    async def test_nvidia_smi_nonzero_exit(self) -> None:
        mock_proc = MagicMock()
        mock_proc.returncode = 1
        mock_proc.stdout = ""
        with patch("engine.performance.thermal.subprocess.run", return_value=mock_proc):
            result = await ThermalMonitor._read_gpu_temp()
            assert result is None


class TestThermalMonitorSample:
    @pytest.mark.asyncio
    async def test_sample_updates_state(self) -> None:
        mon = ThermalMonitor()
        with (
            patch.object(
                ThermalMonitor,
                "_read_cpu_temp",
                new_callable=AsyncMock,
                return_value=85.0,
            ),
            patch.object(
                ThermalMonitor,
                "_read_gpu_temp",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            snap = await mon.sample()
            assert snap.cpu_temp_c == 85.0
            assert snap.gpu_temp_c is None
            assert snap.state == ThermalState.HOT
            assert mon.state == ThermalState.HOT

    @pytest.mark.asyncio
    async def test_sample_normal(self) -> None:
        mon = ThermalMonitor()
        with (
            patch.object(
                ThermalMonitor,
                "_read_cpu_temp",
                new_callable=AsyncMock,
                return_value=50.0,
            ),
            patch.object(
                ThermalMonitor,
                "_read_gpu_temp",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            snap = await mon.sample()
            assert snap.state == ThermalState.NORMAL

    @pytest.mark.asyncio
    async def test_sample_critical(self) -> None:
        mon = ThermalMonitor()
        with (
            patch.object(
                ThermalMonitor,
                "_read_cpu_temp",
                new_callable=AsyncMock,
                return_value=95.0,
            ),
            patch.object(
                ThermalMonitor,
                "_read_gpu_temp",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            snap = await mon.sample()
            assert snap.state == ThermalState.CRITICAL


class TestThermalMonitorCheckThresholds:
    @pytest.mark.asyncio
    async def test_returns_state(self) -> None:
        mon = ThermalMonitor()
        with (
            patch.object(
                ThermalMonitor,
                "_read_cpu_temp",
                new_callable=AsyncMock,
                return_value=60.0,
            ),
            patch.object(
                ThermalMonitor,
                "_read_gpu_temp",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            state = await mon.check_thresholds()
            assert state == ThermalState.NORMAL


class TestThermalMonitorApplyThrottle:
    @pytest.mark.asyncio
    async def test_noop_on_normal(self) -> None:
        mon = ThermalMonitor()
        with (
            patch.object(
                ThermalMonitor,
                "_read_cpu_temp",
                new_callable=AsyncMock,
                return_value=50.0,
            ),
            patch.object(
                ThermalMonitor,
                "_read_gpu_temp",
                new_callable=AsyncMock,
                return_value=None,
            ),
        ):
            result = await mon.apply_throttle()
            assert result == {}

    @pytest.mark.asyncio
    async def test_hot_reduces_threads(self) -> None:
        mon = ThermalMonitor()
        with (
            patch.object(
                ThermalMonitor,
                "_read_cpu_temp",
                new_callable=AsyncMock,
                return_value=85.0,
            ),
            patch.object(
                ThermalMonitor,
                "_read_gpu_temp",
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch.dict("sys.modules", {"torch": MagicMock()}),
        ):
            result = await mon.apply_throttle()
            assert result == {"threads": 1}

    @pytest.mark.asyncio
    async def test_critical_reduces_threads_and_pause(self) -> None:
        mon = ThermalMonitor()
        with (
            patch.object(
                ThermalMonitor,
                "_read_cpu_temp",
                new_callable=AsyncMock,
                return_value=95.0,
            ),
            patch.object(
                ThermalMonitor,
                "_read_gpu_temp",
                new_callable=AsyncMock,
                return_value=None,
            ),
            patch.dict("sys.modules", {"torch": MagicMock()}),
        ):
            result = await mon.apply_throttle()
            assert result == {"threads": 1, "pause": True}
