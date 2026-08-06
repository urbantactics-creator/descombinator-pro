# API Usage Guides

Practical examples and guides for using Descombinator Pro's Python API.

## Programmatic Separation

```python
import asyncio
from pathlib import Path
from engine.audio.loader import AudioLoader
from engine.demucs.separator import DemucsSeparator
from engine.export.writer import AudioWriter

async def separate_file(input_path: Path, output_dir: Path):
    # Load audio
    loader = AudioLoader()
    audio = await loader.load(input_path)

    # Separate
    separator = DemucsSeparator()
    stems = await separator.separate(audio)

    # Export
    writer = AudioWriter()
    await writer.write_stems(stems, output_dir)

asyncio.run(separate_file(Path("song.mp3"), Path("output")))
```

## Custom Audio Processing

```python
from engine.audio.resampler import Resampler
from engine.audio.postprocessor import PostProcessor

# Resample audio
resampler = Resampler(target_sample_rate=44100)
resampled = resampler.process(audio_data)

# Apply post-processing
processor = PostProcessor()
normalized = processor.normalize(resampled)
```

## Performance Monitoring

```python
from engine.performance.monitor import PerformanceMonitor

monitor = PerformanceMonitor()

with monitor.measure("separation"):
    stems = await separator.separate(audio)

print(monitor.get_stats())
```

## Error Handling

```python
from engine.audio.errors import AudioLoadError
from engine.demucs.errors import SeparationError

try:
    audio = await loader.load(path)
except AudioLoadError as e:
    print(f"Failed to load audio: {e}")

try:
    stems = await separator.separate(audio)
except SeparationError as e:
    print(f"Separation failed: {e}")
```

## See Also

- [Python API Reference](python.md) — Auto-generated API docs
- [Architecture Overview](../explanations/architecture/overview.md) — System design
