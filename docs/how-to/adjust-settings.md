# Adjust Settings

Customize Descombinator Pro to match your workflow and hardware.

## Model Selection

Choose the AI model used for separation:

| Model | Description | Best For |
|-------|-------------|----------|
| `htdemucs_ft` | Primary Demucs model | Best overall quality |
| `mdx_extra` | Alternative Demucs model | Different training approach |
| `umxhq` | Open-Unmix model | Alternative separation approach |

**Recommendation:** Start with `htdemucs_ft` (default). Try `mdx_extra` if you want to compare results.

## Output Format

Set the default export format:

- **WAV** (default) — Lossless, best quality
- **FLAC** — Lossless with compression
- **MP3** — Lossy, smaller files
- **M4A** — Lossy, Apple ecosystem

## Performance Settings

### Max Workers

Number of parallel processing workers. Default: CPU count.

- **Higher values:** Faster processing on multi-core CPUs
- **Lower values:** Less memory usage, useful for older hardware

### GPU Acceleration

Automatically used if CUDA is available. No configuration needed.

## Theme

Choose between light and dark themes:

- **Light** — Light theme
- **Dark** (default) — Dark theme

The theme preference is saved and applied on next launch.

## Advanced Settings

### Model Cache Directory

Location where downloaded model weights are stored. Default: `~/.cache/descombinator`

### Logging

- **Log Level:** INFO (default), DEBUG, WARNING, ERROR
- **Log File:** Optional file path for persistent logging

## Tips

- If separation is slow, try increasing **Max Workers** (if you have a multi-core CPU)
- If you run out of memory, decrease **Max Workers**
- Use **WAV** for the highest quality exports
- Enable **dark theme** for reduced eye strain in low-light environments
