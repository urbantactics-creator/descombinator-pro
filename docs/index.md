# Descombinator Pro

Separate any song into vocals and instrumental tracks locally — fast, free, private.
No internet required, no file uploads. Studio-quality results in seconds.

## What is Descombinator Pro?

Descombinator Pro is a desktop application that uses AI to separate audio tracks into **vocals** and **instrumental** stems. All processing happens on your machine — your files never leave your computer.

## Key Features

- **High-quality separation** powered by Demucs (htdemucs_ft, mdx_extra) and Open-Unmix (umxhq)
- **Modern, minimal UI** built with PySide6 — dark/light theme support
- **Fast local processing** with PyTorch acceleration
- **On-device privacy** — no files uploaded to the internet
- **Synchronized multi-track playback** with per-track volume/mute, seek, and gapless mixing
- **Waveform visualization** with playback position tracking
- **Multi-format export** — WAV, FLAC, MP3, M4A with metadata embedding
- **Performance-tested** — 16 benchmark gates enforced in CI
- **Thermal monitoring** — cross-platform CPU/GPU temperature sampling
- **Cross-platform** support (Linux, macOS, Windows)

## Who is this for?

- 🎵 **Musicians** wanting stems for remixing
- 🎬 **Content creators** needing clean instrumentals
- 🎛️ **Producers** needing high-quality stems

## Quick Links

- [Installation](tutorials/installation.md) — Get up and running in minutes
- [Quick Start](tutorials/quick-start.md) — Your first separation in 3 steps
- [How-to Guides](how-to/export-audio.md) — Export, playback, and settings
- [Architecture](explanations/architecture/overview.md) — How it works under the hood
- [API Reference](api/python.md) — Python API documentation

## Project Status

| Milestone | Status |
| ----------- | -------- |
| Vocal ↔ Instrumental separation | ✅ Complete |
| Multi-instrument separation (Demucs) | ✅ Complete |
| Playback & waveform visualization | ✅ Complete |
| Export pipeline (WAV, FLAC, MP3, M4A) | ✅ Complete |
| Performance optimization | ✅ Complete |
| Testing & QA (665 tests) | ✅ Complete |
| Packaging & distribution | ⚠️ In Progress |
| Documentation & release | ⚠️ In Progress |
