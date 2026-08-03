# Troubleshooting

Common issues and solutions for Descombinator Pro.

## Table of Contents

- [Installation Issues](#installation-issues)
- [Runtime Issues](#runtime-issues)
- [Performance Issues](#performance-issues)
- [UI Issues](#ui-issues)
- [Testing Issues](#testing-issues)

## Installation Issues

### PySide6 OpenGL Errors on Linux

**Symptom:** `ImportError: libEGL.so.1: cannot open shared object file` or similar OpenGL errors.

**Solution:** Install system dependencies:

```bash
sudo apt-get install -y libegl1 libgl1 libopengl0 libpulse0
```

### FFmpeg Not Found

**Symptom:** `FileNotFoundError: [Errno 2] No such file or directory: 'ffmpeg'`

**Solution:** Install FFmpeg:

- **Linux:** `sudo apt-get install -y ffmpeg`
- **macOS:** `brew install ffmpeg`
- **Windows:** Download from [ffmpeg.org](https://ffmpeg.org/download.html) and add to PATH

### Python Version Mismatch

**Symptom:** `SyntaxError` or `ImportError` related to Python version.

**Solution:** Ensure Python 3.12+ is installed:

```bash
python --version  # Should be 3.12+
```

### Virtual Environment Issues

**Symptom:** Packages not found or wrong versions installed.

**Solution:** Recreate the virtual environment:

```bash
rm -rf .venv
python -m venv .venv
source .venv/bin/activate
pip install .[dev]
```

## Runtime Issues

### Model Download Fails

**Symptom:** `ConnectionError` or `HTTPError` when loading a separation model.

**Solution:**

1. Check internet connection
2. Verify `MODEL_CACHE_DIR` is writable:
   ```bash
   echo $MODEL_CACHE_DIR
   ls -la ~/.cache/descombinator
   ```
3. Clear the model cache and retry:
   ```bash
   rm -rf ~/.cache/descombinator
   ```

### CUDA Out of Memory

**Symptom:** `torch.cuda.OutOfMemoryError` when using GPU.

**Solution:**

1. Reduce the `segment` parameter in `InferenceConfig` to process smaller chunks
2. Set `MAX_WORKERS=1` to reduce parallel processing
3. Use CPU instead: set `DeviceType.CPU` in settings

### Audio File Not Supported

**Symptom:** `UnsupportedFormatError` when loading a file.

**Solution:** Ensure the file is in a supported format: MP3, WAV, FLAC, M4A, OGG.

Convert if needed:

```bash
ffmpeg -i input.mp4 -ar 44100 -ac 2 output.wav
```

### Separation Produces Poor Quality

**Symptom:** Vocals and instrumental are not well separated.

**Solution:**

1. Try a different model (e.g., `mdx_extra` instead of `htdemucs_ft`)
2. Ensure the input audio is at least 44.1 kHz sample rate
3. Check that the audio is not heavily compressed or noisy

## Performance Issues

### Slow Startup

**Symptom:** Application takes > 3 seconds to start.

**Solution:**

1. Ensure lazy imports are working:
   ```bash
   .venv/bin/python scripts/profiling/measure_startup.py
   ```
2. Check that no heavy imports are at module level
3. Verify `engine/inference/__init__.py` uses PEP 562 `__getattr__`

### High Memory Usage

**Symptom:** Memory usage exceeds 4 GB during separation.

**Solution:**

1. Reduce the `segment` parameter in `InferenceConfig`
2. Use a smaller model (e.g., `htdemucs_ft` instead of `mdx_extra`)
3. Set `MAX_WORKERS=1`
4. Run the memory profiler:
   ```bash
   .venv/bin/python scripts/profiling/profile_memory.py
   ```

### Slow Separation

**Symptom:** Separation takes > 30 seconds for a 3-minute song on CPU.

**Solution:**

1. Check CPU thread count:
   ```bash
   .venv/bin/python -c "import torch; print(torch.get_num_threads())"
   ```
2. Adjust `MAX_WORKERS` environment variable
3. Use GPU if available (CUDA 12+ required)

## UI Issues

### UI Freezes During Processing

**Symptom:** The UI becomes unresponsive during separation.

**Solution:**

1. Ensure separation runs in a `QRunnable` worker, not the main thread
2. Check that `QThreadPool` is used for background tasks
3. Verify progress signals are emitted correctly

### Waveform Not Displaying

**Symptom:** The waveform view is empty or shows incorrect data.

**Solution:**

1. Check that the audio file was loaded successfully
2. Verify the sample rate is correct (44.1 kHz)
3. Check that `WaveformView` receives the correct numpy array

### Playback Not Working

**Symptom:** No audio output during playback.

**Solution:**

1. Check system audio settings
2. Verify `QAudioSink` is initialized correctly
3. Check that the audio buffer is not empty
4. Ensure `AudioMixer` is properly configured

## Testing Issues

### UI Tests Fail in CI

**Symptom:** `pytest tests/ui/` fails with `Qt platform plugin could not be initialized`.

**Solution:**

1. Ensure `QT_QPA_PLATFORM=offscreen` is set:
   ```bash
   QT_QPA_PLATFORM=offscreen pytest tests/ui/
   ```
2. For local testing with display, use `xvfb-run`:
   ```bash
   xvfb-run -a pytest tests/ui/
   ```

### Coverage Threshold Not Met

**Symptom:** CI fails with `Coverage failure: X% < Y%`.

**Solution:**

1. Run coverage locally:
   ```bash
   pytest tests/ --cov=app --cov=engine --cov-report=term-missing
   ```
2. Add tests for uncovered code paths
3. Check that mocks are properly set up

### Benchmark Regression Failures

**Symptom:** CI `benchmark` job fails with `Regression detected`.

**Solution:**

1. Run benchmarks locally:
   ```bash
   pytest benchmarks/ -m "not slow" --benchmark-only
   ```
2. Check if the regression is intentional (from an optimization)
3. If intentional, update baselines:
   ```bash
   pytest benchmarks/ -m "not slow" --benchmark-only --benchmark-json=benchmarks/baselines.json
   ```
4. If unintentional, optimize the code path

## Getting Help

If you encounter an issue not covered here:

1. Check the [GitHub Issues](https://github.com/descombinator/descombinator-pro/issues)
2. Review the [AGENTS.md](../AGENTS.md) for development guidelines
3. Check the [Performance Guide](performance.md) for optimization tips
