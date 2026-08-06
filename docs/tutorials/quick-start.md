# Quick Start

Separate your first audio file into vocals and instrumental tracks in 3 steps.

## Step 1: Launch the Application

```bash
python main.py
```

Or if installed via pip:

```bash
descombinator
```

## Step 2: Load an Audio File

- **Drag and drop** an audio file onto the window, or
- Click the file selection area and choose a file

Supported formats: MP3, WAV, FLAC, M4A, OGG

## Step 3: Separate and Export

1. Click **Separate** to start the AI-powered separation process
2. Wait for the progress dialog to complete
3. Use the playback controls to preview the separated tracks
4. Click **Export** to save the stems to disk

## What Just Happened?

Descombinator Pro uses a pre-trained AI model (Demucs or Open-Unmix) to separate the audio into:

- **Vocals** — The singing/voice track
- **Instrumental** — Everything else (drums, bass, other instruments)

All processing happens locally on your machine. No files are uploaded to the internet.

## Next Steps

- [Feature Walkthrough](feature-walkthrough.md) — Explore all features
- [Export Audio](../how-to/export-audio.md) — Learn about export options
- [Architecture Overview](../explanations/architecture/overview.md) — How it works under the hood
