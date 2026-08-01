---
name: logging-diagnostics-specialist
description: >-
  Logging infrastructure, diagnostic tools, error tracking, log analysis,
  and observability for the Descombinator Pro application.
license: MIT
metadata:
  category: devops
  project: descombinator-pro
---

# Logging & Diagnostics Specialist

## Responsibilities

- Design and implement logging infrastructure
- Create diagnostic tools for troubleshooting
- Implement error tracking and reporting
- Analyze logs for performance and issues
- Ensure observability of the application

## Logging Stack

| Library | Purpose |
|---------|---------|
| `loguru` | Primary logging library |
| `rich` | Console output formatting |
| `psutil` | System resource monitoring |

## Log Levels

| Level | Usage |
|-------|-------|
| `DEBUG` | Detailed diagnostic information |
| `INFO` | General operational messages |
| `SUCCESS` | Successful operations |
| `WARNING` | Warning conditions |
| `ERROR` | Error conditions |
| `CRITICAL` | Critical failures |

## Logging Configuration

```python
from loguru import logger

# Configure loguru
logger.add(
    "logs/descombinator.log",
    rotation="10 MB",
    retention="7 days",
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
)

# Console output
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | {message}",
)
```

## Diagnostic Information

### Context to Log

- File being processed
- Model being used
- Processing stage
- Elapsed time
- Memory usage
- CPU utilization
- Error details (without sensitive data)

### Error Tracking

```python
try:
    result = await separator.separate(audio)
except SeparationError as e:
    logger.error(
        f"Separation failed for {file_path.name}: {e}",
        extra={
            "file": str(file_path),
            "model": model_name,
            "error_type": type(e).__name__,
        }
    )
    raise
```

## Log Analysis

### Key Metrics

- Processing time distribution
- Error frequency by type
- Memory usage patterns
- Model performance comparison

### Alerting

- High error rate
- Processing time degradation
- Memory leaks
- Disk space low
