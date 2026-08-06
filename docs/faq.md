# Frequently Asked Questions

## General

### What is Descombinator Pro?

Descombinator Pro is a desktop application that uses AI to separate audio tracks into **vocals** and **instrumental** stems. All processing happens locally on your machine — your files never leave your computer.

### Is it free?

Yes, Descombinator Pro is free and open-source.

### Do I need an internet connection?

No. All processing happens locally. The only time you need internet is to download the application and model weights (once).

### What audio formats are supported?

MP3, WAV, FLAC, M4A, and OGG.

## Installation

### What are the system requirements?

- **Python 3.12+** (if installing from source)
- **FFmpeg** for audio decoding/encoding
- **4 GB RAM** minimum, 8 GB recommended
- **CUDA-capable GPU** optional (speeds up separation)

### How do I install FFmpeg?

| Platform | Command |
|----------|---------|
| **Ubuntu/Debian** | `sudo apt-get install -y ffmpeg` |
| **macOS** | `brew install ffmpeg` |
| **Windows** | Download from [ffmpeg.org](https://ffmpeg.org/download.html) |

### Can I use a pre-built installer?

Yes, prebuilt installers are available for Linux (AppImage), Windows (Inno Setup), and macOS (app bundle). Check the [Releases](https://github.com/descombinator/descombinator/releases) page.

## Usage

### How long does separation take?

| Hardware | 3-minute song |
|----------|---------------|
| CPU (8 cores) | ~15-30 seconds |
| GPU (CUDA) | ~5-10 seconds |

### Which model should I use?

Start with `htdemucs_ft` (default). It provides the best overall quality. Try `mdx_extra` if you want to compare results.

### Can I separate into more than 2 tracks?

Yes, Demucs can separate into 4 stems: vocals, drums, bass, and other. This is available in the multi-instrument separation mode.

### How do I export the separated tracks?

Click the **Export** button after separation. Choose your format (WAV, FLAC, MP3, M4A), sample rate, and other options.

## Troubleshooting

### The app is slow

- Check that you're using the `htdemucs_ft` model (fastest)
- Increase **Max Workers** in Settings if you have a multi-core CPU
- Use GPU acceleration if you have a CUDA-capable GPU

### I get an "Out of memory" error

- Decrease **Max Workers** in Settings
- Close other applications to free up RAM
- Try processing shorter audio files

### The separation quality is poor

- Try a different model (`mdx_extra` or `umxhq`)
- Ensure your source audio is high quality (not heavily compressed)
- Check that the audio is well-mixed (not too much reverb or effects)

### FFmpeg is not found

Make sure FFmpeg is installed and in your PATH. Run `ffmpeg -version` to verify.

## Development

### How do I contribute?

See the [Development Guide](development/development.md) for setup instructions and the contribution workflow.

### How do I run the tests?

```bash
pytest tests/
```

### How do I build from source?

```bash
pip install -e ".[dev]"
python main.py
```
