"""Unit tests for engine.demucs.config — SeparationConfig and enums."""

import pytest
from pydantic import ValidationError

from engine.demucs.config import (
    DeviceType,
    ModelName,
    SeparationConfig,
    SplitMode,
)


class TestModelName:
    def test_htdemucs_ft(self) -> None:
        assert ModelName.HTDEMUCS_FT == "htdemucs_ft"

    def test_mdx_extra(self) -> None:
        assert ModelName.MDX_EXTRA == "mdx_extra"

    def test_umxhq(self) -> None:
        assert ModelName.UMXHQ == "umxhq"

    def test_coerce_from_string(self) -> None:
        assert ModelName("htdemucs_ft") == ModelName.HTDEMUCS_FT


class TestDeviceType:
    def test_cpu(self) -> None:
        assert DeviceType.CPU == "cpu"

    def test_cuda(self) -> None:
        assert DeviceType.CUDA == "cuda"


class TestSplitMode:
    def test_segment(self) -> None:
        assert SplitMode.SEGMENT == "segment"

    def test_full(self) -> None:
        assert SplitMode.FULL == "full"


class TestSeparationConfig:
    def test_defaults(self) -> None:
        cfg = SeparationConfig()
        assert cfg.model_name == ModelName.HTDEMUCS_FT
        assert cfg.device == DeviceType.CPU
        assert cfg.shifts == 1
        assert cfg.overlap == 0.25
        assert cfg.split_mode == SplitMode.SEGMENT
        assert cfg.segment is None
        assert cfg.jobs == 0
        assert cfg.mixed_precision is False
        assert cfg.pin_memory is False
        assert cfg.output_stems == ["vocals", "drums", "bass", "other"]

    def test_custom_values(self) -> None:
        cfg = SeparationConfig(
            model_name=ModelName.UMXHQ,
            device=DeviceType.CUDA,
            shifts=5,
            overlap=0.5,
            split_mode=SplitMode.FULL,
            segment=30,
            jobs=4,
            mixed_precision=True,
            pin_memory=True,
            output_stems=["vocals", "drums"],
        )
        assert cfg.model_name == ModelName.UMXHQ
        assert cfg.device == DeviceType.CUDA
        assert cfg.shifts == 5
        assert cfg.overlap == 0.5
        assert cfg.split_mode == SplitMode.FULL
        assert cfg.segment == 30
        assert cfg.jobs == 4
        assert cfg.mixed_precision is True
        assert cfg.pin_memory is True
        assert cfg.output_stems == ["vocals", "drums"]

    def test_shifts_too_high_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SeparationConfig(shifts=11)

    def test_shifts_negative_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SeparationConfig(shifts=-1)

    def test_overlap_out_of_range_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SeparationConfig(overlap=1.5)

    def test_negative_overlap_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SeparationConfig(overlap=-0.1)

    def test_negative_jobs_rejected(self) -> None:
        with pytest.raises(ValidationError):
            SeparationConfig(jobs=-1)

    def test_serialization_roundtrip(self) -> None:
        cfg = SeparationConfig(shifts=3, overlap=0.75)
        data = cfg.model_dump()
        restored = SeparationConfig(**data)
        assert restored == cfg
