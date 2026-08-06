# Module Interface Contracts

This document defines the public interfaces (contracts) for each module in Descombinator Pro.

## engine/ Layer

### engine/audio/

#### AudioLoader

```python
class AudioLoader:
    """Load and preprocess audio files for separation."""

    async def load(
        self, path: Path, sr: int = 44100, mono: bool = True
    ) -> np.ndarray:
        """Load an audio file and return a numpy array.

        Args:
            path: Path to the audio file.
            sr: Target sample rate (default: 44100).
            mono: Convert to mono (default: True).

        Returns:
            Audio data as a 1D numpy array (mono) or 2D array (stereo).

        Raises:
            FileNotFoundError: If the file does not exist.
            UnsupportedFormatError: If the format is not supported.
            AudioLoadError: If loading fails.
        """

    def validate_exists(self, path: Path) -> None:
        """Validate that the file exists."""

    def validate_format(self, path: Path) -> None:
        """Validate that the file format is supported."""
```

#### AudioResampler

```python
class AudioResampler:
    """Resample audio to a target sample rate."""

    async def resample(
        self, audio: np.ndarray, sr: int, target_sr: int = 44100
    ) -> np.ndarray:
        """Resample audio to the target sample rate.

        Args:
            audio: Input audio array.
            sr: Current sample rate.
            target_sr: Target sample rate (default: 44100).

        Returns:
            Resampled audio array.
        """
```

#### AudioPreprocessor

```python
class AudioPreprocessor:
    """Preprocess audio for separation."""

    async def preprocess(
        self, audio: np.ndarray, sr: int = 44100
    ) -> np.ndarray:
        """Apply DC offset removal and peak normalization.

        Args:
            audio: Input audio array.
            sr: Sample rate (default: 44100).

        Returns:
            Preprocessed audio array.
        """
```

#### AudioPostprocessor

```python
class AudioPostprocessor:
    """Postprocess separated audio stems."""

    async def postprocess(
        self, stems: dict[str, np.ndarray], sr: int = 44100
    ) -> dict[str, np.ndarray]:
        """Apply artifact reduction and peak limiting to stems.

        Args:
            stems: Dictionary of stem name to audio array.
            sr: Sample rate (default: 44100).

        Returns:
            Postprocessed stems dictionary.
        """
```

#### MetadataReader

```python
class MetadataReader:
    """Read metadata from audio files."""

    async def read(self, path: Path) -> AudioMetadata:
        """Read metadata from an audio file.

        Args:
            path: Path to the audio file.

        Returns:
            AudioMetadata object with title, artist, album, etc.
        """
```

#### MetadataWriter

```python
class MetadataWriter:
    """Write metadata to audio files."""

    async def write(
        self, path: Path, metadata: AudioMetadata
    ) -> None:
        """Write metadata to an audio file.

        Args:
            path: Path to the audio file.
            metadata: Metadata to write.
        """
```

### engine/inference/

#### SeparationModel (Protocol)

```python
class SeparationModel(Protocol):
    """Protocol for separation model backends."""

    async def initialize(self) -> None:
        """Initialize the model (lazy loading)."""

    async def separate(
        self, audio: torch.Tensor
    ) -> dict[str, torch.Tensor]:
        """Separate audio into stems.

        Args:
            audio: Input audio tensor.

        Returns:
            Dictionary of stem name to audio tensor.
        """

    @property
    def sources(self) -> list[str]:
        """Return the list of source names."""
```

#### DemucsAgent

```python
class DemucsAgent:
    """Demucs separation model agent."""

    def __init__(self, config: InferenceConfig) -> None:
        """Initialize the Demucs agent.

        Args:
            config: Inference configuration.
        """

    async def initialize(self) -> None:
        """Lazy-load the Demucs model."""

    async def separate(
        self, audio: torch.Tensor
    ) -> dict[str, torch.Tensor]:
        """Separate audio using Demucs.

        Args:
            audio: Input audio tensor.

        Returns:
            Dictionary of stem name to audio tensor.
        """

    @property
    def sources(self) -> list[str]:
        """Return the list of source names."""
```

#### OpenUnmixAgent

```python
class OpenUnmixAgent:
    """Open-Unmix separation model agent."""

    def __init__(self, config: InferenceConfig) -> None:
        """Initialize the Open-Unmix agent.

        Args:
            config: Inference configuration.
        """

    async def initialize(self) -> None:
        """Lazy-load the Open-Unmix model."""

    async def separate(
        self, audio: torch.Tensor
    ) -> dict[str, torch.Tensor]:
        """Separate audio using Open-Unmix.

        Args:
            audio: Input audio tensor.

        Returns:
            Dictionary of stem name to audio tensor.
        """

    @property
    def sources(self) -> list[str]:
        """Return the list of source names."""
```

#### InferencePipeline

```python
class InferencePipeline:
    """Orchestrate the inference process."""

    def __init__(self, config: InferenceConfig) -> None:
        """Initialize the inference pipeline.

        Args:
            config: Inference configuration.
        """

    async def run(
        self, audio: np.ndarray, sr: int = 44100
    ) -> dict[str, np.ndarray]:
        """Run the full inference pipeline.

        Args:
            audio: Input audio array.
            sr: Sample rate (default: 44100).

        Returns:
            Dictionary of stem name to audio array.
        """
```

#### ModelManager

```python
class ModelManager:
    """Manage separation models with lazy loading and caching."""

    def __init__(self, config: InferenceConfig) -> None:
        """Initialize the model manager.

        Args:
            config: Inference configuration.
        """

    async def get_model(self, name: str) -> SeparationModel:
        """Get a model by name, creating and caching if needed.

        Args:
            name: Model name.

        Returns:
            SeparationModel instance.

        Raises:
            ModelNotFoundError: If the model name is not recognized.
        """

    def clear_cache(self) -> None:
        """Clear the model cache."""
```

### engine/demucs/

#### DemucsSeparator

```python
class DemucsSeparator:
    """Orchestrate the full separation workflow."""

    def __init__(
        self,
        pipeline: InferencePipeline,
        preprocessor: AudioPreprocessor,
        postprocessor: AudioPostprocessor,
        config: SeparationConfig,
    ) -> None:
        """Initialize the separator.

        Args:
            pipeline: Inference pipeline.
            preprocessor: Audio preprocessor.
            postprocessor: Audio postprocessor.
            config: Separation configuration.
        """

    async def separate(
        self, audio: np.ndarray, sr: int = 44100
    ) -> SeparationResult:
        """Run the full separation workflow.

        Args:
            audio: Input audio array.
            sr: Sample rate (default: 44100).

        Returns:
            SeparationResult with stems and metadata.
        """
```

### engine/export/

#### ExportWriter

```python
class ExportWriter:
    """Write separated stems to files."""

    def __init__(self, config: ExportConfig) -> None:
        """Initialize the export writer.

        Args:
            config: Export configuration.
        """

    async def write_stem(
        self,
        stem_name: str,
        audio: np.ndarray,
        output_path: Path,
        sample_rate: int = 44100,
    ) -> None:
        """Write a single stem to a file.

        Args:
            stem_name: Name of the stem.
            audio: Audio data.
            output_path: Output file path.
            sample_rate: Sample rate (default: 44100).

        Raises:
            WriteError: If writing fails.
            UnsupportedFormatError: If the format is not supported.
        """
```

#### BatchExporter

```python
class BatchExporter:
    """Export all stems in batch with progress tracking."""

    def __init__(
        self,
        writer: ExportWriter,
        config: ExportConfig,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> None:
        """Initialize the batch exporter.

        Args:
            writer: Export writer instance.
            config: Export configuration.
            progress_callback: Optional callback for progress updates.
        """

    async def export_all(
        self,
        stems: dict[str, np.ndarray],
        output_dir: Path,
        sample_rate: int = 44100,
    ) -> list[Path]:
        """Export all stems to files.

        Args:
            stems: Dictionary of stem name to audio array.
            output_dir: Output directory.
            sample_rate: Sample rate (default: 44100).

        Returns:
            List of output file paths.
        """
```

### engine/performance/

#### ResourceMonitor

```python
class ResourceMonitor:
    """Monitor system resources (CPU, memory, disk)."""

    def __init__(self, interval: float = 1.0) -> None:
        """Initialize the resource monitor.

        Args:
            interval: Sampling interval in seconds.
        """

    async def start(self) -> None:
        """Start monitoring."""

    async def stop(self) -> None:
        """Stop monitoring."""

    def summary(self) -> dict[str, float]:
        """Return a summary of resource usage."""
```

## app/ Layer

### app/services/

#### SeparationService

```python
class SeparationService:
    """Orchestrate the separation pipeline."""

    def __init__(
        self,
        demucs_agent: DemucsAgent,
        audio_loader: AudioLoader,
    ) -> None:
        """Initialize the separation service.

        Args:
            demucs_agent: Demucs agent for inference.
            audio_loader: Audio loader for file I/O.
        """

    async def separate(self, file_path: Path) -> SeparationResult:
        """Separate an audio file into stems.

        Args:
            file_path: Path to the input audio file.

        Returns:
            SeparationResult with stems and metadata.
        """

    async def separate_loaded(
        self, audio: np.ndarray, sr: int = 44100
    ) -> SeparationResult:
        """Separate already-loaded audio data.

        Args:
            audio: Input audio array.
            sr: Sample rate (default: 44100).

        Returns:
            SeparationResult with stems and metadata.
        """
```

#### PlaybackService

```python
class PlaybackService:
    """Orchestrate audio playback."""

    def __init__(self) -> None:
        """Initialize the playback service."""

    def load_file(self, file_path: Path) -> None:
        """Load an audio file for playback.

        Args:
            file_path: Path to the audio file.
        """

    def set_stems(
        self, stems: dict[str, np.ndarray], sample_rate: int = 44100
    ) -> None:
        """Set the stems for playback.

        Args:
            stems: Dictionary of stem name to audio array.
            sample_rate: Sample rate (default: 44100).
        """

    def set_track_volume(self, track: str, volume: float) -> None:
        """Set the volume for a specific track.

        Args:
            track: Track name.
            volume: Volume level (0.0 to 1.0).
        """

    def set_track_mute(self, track: str, muted: bool) -> None:
        """Mute or unmute a specific track.

        Args:
            track: Track name.
            muted: Whether to mute the track.
        """

    def play(self) -> None:
        """Start playback."""

    def pause(self) -> None:
        """Pause playback."""

    def stop(self) -> None:
        """Stop playback."""

    def seek(self, position: float) -> None:
        """Seek to a position in the audio.

        Args:
            position: Position in seconds.
        """
```

#### ExportService

```python
class ExportService:
    """Orchestrate the export pipeline."""

    def __init__(
        self,
        writer: ExportWriter,
        batch_exporter: BatchExporter,
    ) -> None:
        """Initialize the export service.

        Args:
            writer: Export writer instance.
            batch_exporter: Batch exporter instance.
        """

    async def export_stems(
        self,
        stems: dict[str, np.ndarray],
        output_dir: Path,
        config: ExportConfig,
    ) -> list[Path]:
        """Export stems to files.

        Args:
            stems: Dictionary of stem name to audio array.
            output_dir: Output directory.
            config: Export configuration.

        Returns:
            List of output file paths.
        """
```

### app/models/

#### AppState

```python
class AppState(BaseModel):
    """Application state model."""

    status: SeparationStatus = SeparationStatus.IDLE
    current_file: Path | None = None
    stems: dict[str, np.ndarray] | None = None
    sample_rate: int = 44100
    progress: float = 0.0
    progress_message: str = ""
    error: str | None = None
```

#### SettingsModel

```python
class SettingsModel(BaseModel):
    """Application settings model."""

    model_name: str = "htdemucs_ft"
    export_format: str = "wav"
    sample_rate: int = 44100
    bit_depth: int = 16
    bitrate: int = 192000
    normalize: bool = True
    fade_in: float = 0.0
    fade_out: float = 0.0
    theme: str = "dark"
    max_workers: int = 4
```

### app/controllers/

#### MainController

```python
class MainController(QObject):
    """Main application controller."""

    separation_started = Signal()
    separation_progress = Signal(int, str)
    separation_completed = Signal(object)
    separation_error = Signal(str)

    def __init__(
        self,
        separation_service: SeparationService,
        export_service: ExportService,
        settings: SettingsModel,
    ) -> None:
        """Initialize the main controller."""

    async def handle_separate_requested(self, file_path: Path) -> None:
        """Handle a separation request."""

    def handle_export_requested(
        self, output_dir: Path, config: ExportConfig
    ) -> None:
        """Handle an export request."""
```

#### PlaybackController

```python
class PlaybackController(QObject):
    """Playback controller."""

    playback_state_changed = Signal(str)
    position_changed = Signal(float)
    duration_changed = Signal(float)

    def __init__(self, playback_service: PlaybackService) -> None:
        """Initialize the playback controller."""

    def load_stems(
        self, stems: dict[str, np.ndarray], sample_rate: int = 44100
    ) -> None:
        """Load stems for playback."""

    def play(self) -> None:
        """Start playback."""

    def pause(self) -> None:
        """Pause playback."""

    def stop(self) -> None:
        """Stop playback."""

    def seek(self, position: float) -> None:
        """Seek to a position."""

    def set_track_volume(self, track: str, volume: float) -> None:
        """Set track volume."""

    def set_track_mute(self, track: str, muted: bool) -> None:
        """Mute/unmute a track."""
```

#### SettingsController

```python
class SettingsController(QObject):
    """Settings controller."""

    settings_changed = Signal()

    def __init__(self, settings: SettingsModel) -> None:
        """Initialize the settings controller."""

    def load_settings(self) -> SettingsModel:
        """Load settings from disk."""

    def save_settings(self, settings: SettingsModel) -> None:
        """Save settings to disk."""

    def update_setting(self, key: str, value: Any) -> None:
        """Update a single setting."""
```

## Data Models

### SeparationResult

```python
class SeparationResult(BaseModel):
    """Result of a separation operation."""

    stems: dict[str, np.ndarray]
    sample_rate: int
    duration: float
    metadata: AudioMetadata | None = None
    model_name: str
    processing_time: float
```

### AudioMetadata

```python
class AudioMetadata(BaseModel):
    """Audio file metadata."""

    title: str | None = None
    artist: str | None = None
    album: str | None = None
    year: int | None = None
    genre: str | None = None
    artwork: bytes | None = None
```

### InferenceConfig

```python
class InferenceConfig(BaseModel):
    """Inference configuration."""

    model_name: ModelName = ModelName.HTDEMUCS_FT
    device: DeviceType = DeviceType.CPU
    segment: float = 10.0
    overlap: float = 0.25
    progress: bool = True
```

### SeparationConfig

```python
class SeparationConfig(BaseModel):
    """Separation configuration."""

    model_name: ModelName = ModelName.HTDEMUCS_FT
    device: DeviceType = DeviceType.CPU
    segment: float = 10.0
    overlap: float = 0.25
    progress: bool = True
```

### ExportConfig

```python
class ExportConfig(BaseModel):
    """Export configuration."""

    format: ExportFormat = ExportFormat.WAV
    sample_rate: int = Field(default=44100, ge=8000, le=192000)
    bit_depth: int = Field(default=16, ge=8, le=32)
    bitrate: int = Field(default=192000, ge=32000, le=320000)
    normalize: bool = True
    fade_in: float = Field(default=0.0, ge=0.0, le=10.0)
    fade_out: float = Field(default=0.0, ge=0.0, le=10.0)
    metadata: ExportMetadata | None = None
```

## Enums

### SeparationStatus

```python
class SeparationStatus(Enum):
    IDLE = "idle"
    LOADING = "loading"
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"
```

### ModelName

```python
class ModelName(StrEnum):
    HTDEMUCS_FT = "htdemucs_ft"
    MDX_EXTRA = "mdx_extra"
    UMXHQ = "umxhq"
```

### DeviceType

```python
class DeviceType(StrEnum):
    CPU = "cpu"
    CUDA = "cuda"
```

### ExportFormat

```python
class ExportFormat(StrEnum):
    WAV = "wav"
    FLAC = "flac"
    MP3 = "mp3"
    M4A = "m4a"
```
