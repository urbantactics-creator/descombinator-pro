---
name: audio-separation-specialist
description: >-
  Audio source separation techniques, model selection, quality evaluation,
  artifact reduction, and separation algorithm optimization.
license: MIT
metadata:
  category: ml
  project: descombinator-pro
---

# Audio Separation Specialist

## Responsibilities

- Select and configure separation models for optimal quality
- Implement artifact reduction techniques
- Evaluate separation quality using objective and subjective metrics
- Tune model hyperparameters for different audio types
- Research and integrate new separation techniques

## Separation Models

### Demucs v4 (Primary)

- **Architecture**: Deep LSTM with temporal convolutions
- **Strengths**: Excellent vocal separation, low artifacts
- **Sample Rate**: 44.1 kHz
- **Stems**: Vocals, Drums, Bass, Other

### Open-Unmix (Secondary)

- **Architecture**: U-Net with spectrogram masking
- **Strengths**: Good for music with clear instrument separation
- **Sample Rate**: 44.1 kHz
- **Stems**: Vocals, Drums, Bass, Other

## Quality Evaluation

### Objective Metrics

| Metric | Description | Target |
|--------|-------------|--------|
| SDR | Signal-to-Distortion Ratio | >5 dB |
| SIR | Signal-to-Interference Ratio | >10 dB |
| SAR | Signal-to-Artifact Ratio | >10 dB |
| PESQ | Perceptual Evaluation of Speech Quality | >3.0 |

### Subjective Evaluation

- Conduct listening tests with reference tracks
- Gather user feedback on separation quality
- Compare against baseline (Spleeter, Open-Unmix)

## Artifact Reduction

### Common Artifacts

1. **Musical Noise** — Residual artifacts in silent regions
2. **Phase Issues** — Phase cancellation between stems
3. **Leakage** — Vocals bleeding into instrumental
4. **Transient Smearing** — Loss of attack transients

### Mitigation Techniques

- Apply Wiener filtering post-separation
- Use spectral masking with overlap-add
- Implement phase-aware processing
- Apply adaptive noise reduction
