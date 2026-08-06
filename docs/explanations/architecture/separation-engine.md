# Separation Engine

How Descombinator Pro separates audio into stems using AI models.

## Supported Models

### Demucs

Demucs is a deep learning model for music source separation developed by Meta.

| Model | Description |
|-------|-------------|
| `htdemucs_ft` | Primary model — high-quality Demucs separation with fine-tuning |
| `mdx_extra` | Alternative model — high-quality Demucs with different training data |

### Open-Unmix

Open-Unmix is a popular open-source model for music source separation.

| Model | Description |
|-------|-------------|
| `umxhq` | Open-Unmix model — alternative separation approach |

## Separation Pipeline

1. **Load Audio:** Audio file is loaded and decoded using `librosa`/`soundfile`
2. **Resample:** Audio is resampled to the target sample rate (default: 44100 Hz)
3. **Preprocess:** Audio is converted to the format expected by the model
4. **Inference:** The model separates the audio into stems
5. **Postprocess:** Stems are converted back to audio format
6. **Export:** Stems are saved to disk in the selected format

## Model Architecture

### Demucs

Demucs uses a U-Net architecture with:

- **Encoder:** Convolutional layers that extract features
- **Bottleneck:** Dense layers that process features
- **Decoder:** Transposed convolutions that reconstruct audio
- **Skip connections:** Preserve detail across layers

### Open-Unmix

Open-Unmix uses a bi-directional LSTM with:

- **Input:** Magnitude spectrogram
- **LSTM:** Bidirectional LSTM layers
- **Output:** Mask for each source

## Performance

| Hardware | 3-minute song |
|----------|---------------|
| CPU (8 cores) | ~15-30 seconds |
| GPU (CUDA) | ~5-10 seconds |

## Quality

The separation quality depends on:

- **Model:** `htdemucs_ft` generally produces the best results
- **Source material:** Clean, well-mixed audio separates better
- **Sample rate:** Higher sample rates preserve more detail

## See Also

- [Architecture Overview](overview.md)
- [Performance Optimization](performance-optimization.md)
- [Tech Stack](../tech-stack.md)
