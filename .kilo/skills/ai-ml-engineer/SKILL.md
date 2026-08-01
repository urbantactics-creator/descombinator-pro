---
name: ai-ml-engineer
description: >-
  Machine learning model integration, PyTorch optimization, inference pipeline
  design, and model performance tuning for Descombinator Pro.
license: MIT
metadata:
  category: ml
  project: descombinator-pro
---

# AI/ML Engineer

## Responsibilities

- Integrate and optimize ML models (Demucs, Open-Unmix) for audio separation
- Optimize PyTorch inference for CPU and GPU
- Design the inference pipeline in `engine/inference/`
- Manage model weights and versioning
- Profile and tune model performance

## Model Stack

| Model | Purpose | Backend |
|-------|---------|---------|
| Demucs v4 | Vocal/instrumental separation | PyTorch |
| Open-Unmix | Alternative separation | PyTorch |
| (Future) Hybrid | Multi-instrument separation | ONNX Runtime |

## Inference Optimization

### CPU Optimization

- Use `torch.set_num_threads()` based on CPU core count
- Enable `torch.backends.mkldnn` for Intel CPUs
- Consider `torch.compile()` for PyTorch 2.x+

### GPU Optimization

- Use `torch.cuda.amp.autocast()` for mixed precision
- Pin memory for faster CPU↔GPU transfers
- Batch processing for multiple files

## Pipeline Design

```
Audio Input → Preprocessing → Model Inference → Postprocessing → Stems Output
```

### Preprocessing

- Resample to model's expected sample rate (44.1 kHz for Demucs)
- Convert to mono if needed
- Normalize audio levels

### Postprocessing

- Apply windowing to reduce artifacts
- Optional denoising filter
- Format output to match input quality

## Model Management

- Store model weights in `engine/inference/weights/`
- Use `huggingface_hub` for model downloads
- Cache models locally to avoid re-downloads
- Verify model integrity with checksums
