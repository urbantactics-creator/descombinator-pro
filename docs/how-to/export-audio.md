# Export Audio

Learn how to export separated tracks in different formats and with custom settings.

## Supported Formats

| Format | Quality | Use Case |
|--------|---------|----------|
| WAV | Lossless, 16/24-bit PCM | Professional use |
| FLAC | Lossless, compression level 5 | Archiving |
| MP3 | Lossy, 192–320 kbps VBR | Sharing |
| M4A | Lossy, AAC encoding | Apple ecosystem |

## Export Options

### Format Selection

Choose the output format in the export dialog or set a default in **Settings** → **Output Format**. All export options (sample rate, bit depth, bitrate, normalization, fades) are configured in **Settings** and applied automatically at export time.

### Sample Rate

Set the output sample rate from 8000 to 192000 Hz. Default: 44100 Hz.

### Bit Depth

For WAV and FLAC, choose the bit depth (8–32 bits). Default: 16 bits.

### Bitrate

For MP3 and M4A, choose the bitrate (32–320 kbps). Default: 192 kbps.

### Normalization

Enable peak normalization to -1 dBFS to ensure consistent volume across tracks.

### Fade In/Out

Apply fade-in and fade-out effects (0–10 seconds) to avoid clicks at the start and end of tracks.

### Metadata

Embed metadata into the exported files:
- Title
- Artist
- Album
- Artwork (cover image)

## Batch Export

All separated stems are exported together. The output directory will contain:

```
output/
├── vocals.wav
├── instrumental.wav
├── drums.wav
├── bass.wav
└── other.wav
```

## Tips

- Use **WAV** or **FLAC** for professional use or archiving
- Use **MP3** or **M4A** for sharing or portable devices
- Enable **normalization** if you want consistent volume across different source files
- Add **metadata** to make your music library organized
