"""Unit tests for engine.inference.config — InferenceConfig and enums."""

import pytest
from pydantic import ValidationError

from engine.inference.config import DeviceType, InferenceConfig, ModelName


class TestModelNameInference:
    def test_values(self) -> None:
        assert ModelName.HTDEMUCS_FT == "htdemucs_ft"
        assert ModelName.MDX_EXTRA == "mdx_extra"
        assert ModelName.UMXHQ == "umxhq"

    def test_count(self) -> None:
        assert len(ModelName) == 3


class TestDeviceTypeInference:
    def test_values(self) -> None:
        assert DeviceType.CPU == "cpu"
        assert DeviceType.CUDA == "cuda"


class TestInferenceConfig:
    def test_defaults(self) -> None:
        cfg = InferenceConfig()
        assert cfg.model_name == ModelName.HTDEMUCS_FT
        assert cfg.device == DeviceType.CPU
        assert cfg.shifts == 1
        assert cfg.overlap == 0.25
        assert cfg.segment is None
        assert cfg.jobs == 0
        assert cfg.mixed_precision is False
        assert cfg.pin_memory is False
        assert cfg.target_stems == ["vocals", "other"]

    def test_custom_values(self) -> None:
        cfg = InferenceConfig(
            model_name=ModelName.UMXHQ,
            device=DeviceType.CUDA,
            shifts=3,
            overlap=0.5,
            segment=60,
            jobs=2,
            mixed_precision=True,
            pin_memory=True,
            target_stems=["vocals"],
        )
        assert cfg.model_name == ModelName.UMXHQ
        assert cfg.shifts == 3
        assert cfg.target_stems == ["vocals"]

    def test_shifts_validation_too_high(self) -> None:
        with pytest.raises(ValidationError):
            InferenceConfig(shifts=11)

    def test_shifts_validation_negative(self) -> None:
        with pytest.raises(ValidationError):
            InferenceConfig(shifts=-1)

    def test_overlap_validation_too_high(self) -> None:
        with pytest.raises(ValidationError):
            InferenceConfig(overlap=1.1)

    def test_overlap_validation_negative(self) -> None:
        with pytest.raises(ValidationError):
            InferenceConfig(overlap=-0.1)

    def test_jobs_validation_negative(self) -> None:
        with pytest.raises(ValidationError):
            InferenceConfig(jobs=-1)

    def test_serialization_roundtrip(self) -> None:
        cfg = InferenceConfig(model_name=ModelName.MDX_EXTRA, shifts=5)
        data = cfg.model_dump()
        restored = InferenceConfig(**data)
        assert restored == cfg
