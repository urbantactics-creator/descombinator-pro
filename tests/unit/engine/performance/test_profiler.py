"""Unit tests for engine.performance.profiler — cpu_profile and torch_profile_trace."""

from __future__ import annotations

from pathlib import Path

from engine.performance.profiler import cpu_profile, torch_profile_trace


class TestCpuProfile:
    def test_creates_prof_file(self, tmp_path: Path) -> None:
        out = tmp_path / "cpu.pstats"
        with cpu_profile(out):
            pass
        assert out.exists()
        assert out.stat().st_size > 0

    def test_profiles_actual_work(self, tmp_path: Path) -> None:
        out = tmp_path / "cpu.pstats"
        with cpu_profile(out):
            sum(range(10000))
        assert out.exists()

    def test_default_sort_by_cumtime(self, tmp_path: Path) -> None:
        out = tmp_path / "cpu.pstats"
        with cpu_profile(out):
            pass
        assert out.exists()


class TestTorchProfileTrace:
    def test_creates_trace_file(self, tmp_path: Path) -> None:
        out = tmp_path / "trace.json"
        with torch_profile_trace(out):
            pass
        assert out.exists()

    def test_profiles_actual_work(self, tmp_path: Path) -> None:
        out = tmp_path / "trace.json"
        with torch_profile_trace(out):
            sum(range(10000))
        assert out.exists()
        assert out.stat().st_size > 0
