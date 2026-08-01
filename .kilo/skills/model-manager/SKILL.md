---
name: model-manager
description: >-
  ML model lifecycle management, model downloading, caching, versioning,
  and model switching for the Descombinator Pro separation engine.
license: MIT
metadata:
  category: ml
  project: descombinator-pro
---

# Model Manager

## Responsibilities

- Manage ML model lifecycle (download, cache, version, switch)
- Handle model weights storage and integrity verification
- Implement model switching UI
- Monitor model performance and resource usage
- Handle model updates and migrations

## Model Registry

| Model | Version | Size | Source |
|-------|---------|------|--------|
| Demucs v4 | htdemucs_ft | ~120 MB | HuggingFace |
| Demucs v4 | mdx_extra | ~200 MB | HuggingFace |
| Open-Unmix | umxhq | ~50 MB | HuggingFace |
| (Future) Demucs v5 | - | - | - |

## Model Storage

```
engine/inference/weights/
├── demucs/
│   ├── htdemucs_ft/
│   │   ├── model.pt
│   │   └── config.json
│   └── mdx_extra/
│       ├── model.pt
│       └── config.json
├── openunmix/
│   └── umxhq/
│       ├── model.pt
│       └── config.json
└── cache/
    └── (downloaded models)
```

## Model Lifecycle

### Download

```python
from huggingface_hub import hf_hub_download

def download_model(model_name: str, filename: str) -> Path:
    return Path(hf_hub_download(
        repo_id=f"facebook/{model_name}",
        filename=filename,
        cache_dir=str(MODEL_CACHE_DIR)
    ))
```

### Cache Management

- Cache models in user data directory
- Verify model integrity with SHA256 checksums
- Clean up old model versions
- Pre-download models during installation

### Versioning

- Track model version in config
- Support model rollback
- Migrate user settings when model changes
- Display model info in UI

## Model Switching

### UI Integration

- Dropdown in Settings to select model
- Display model size and expected quality
- Show download progress for new models
- Warn user about model switching impact

### Runtime Switching

```python
class ModelManager:
    def __init__(self):
        self._current_model: SeparationModel | None = None
        self._model_cache: dict[str, SeparationModel] = {}

    async def switch_model(self, model_name: str) -> None:
        if model_name not in self._model_cache:
            self._model_cache[model_name] = await self._load_model(model_name)
        self._current_model = self._model_cache[model_name]
```

## Performance Monitoring

- Track inference time per model
- Monitor memory usage
- Log model performance metrics
- Alert on performance degradation
