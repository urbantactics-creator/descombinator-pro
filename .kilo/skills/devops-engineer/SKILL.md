---
name: devops-engineer
description: >-
  CI/CD pipeline setup, automated testing, deployment automation, infrastructure
  as code, and monitoring for the Descombinator Pro project.
license: MIT
metadata:
  category: devops
  project: descombinator-pro
---

# DevOps Engineer

## Responsibilities

- Set up CI/CD pipelines for automated testing and building
- Configure automated testing on multiple platforms
- Implement deployment automation
- Monitor application health and performance
- Manage infrastructure for development and testing

## CI/CD Pipeline

### GitHub Actions

```yaml
# .github/workflows/ci.yml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
        python: [3.12]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python }}
      - run: pip install -r requirements.txt
      - run: pytest tests/
```

### Build Pipeline

```yaml
# .github/workflows/build.yml
name: Build
on:
  release:
    types: [published]
jobs:
  build:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest, macos-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: 3.12
      - run: pip install -r requirements.txt pyinstaller
      - run: pyinstaller --onefile --windowed descombinator.spec
      - uses: actions/upload-artifact@v4
        with:
          name: descombinator-${{ matrix.os }}
          path: dist/
```

## Testing Matrix

| Platform | Python | Tests |
|----------|--------|-------|
| Ubuntu 22.04 | 3.12 | Unit, integration, UI |
| Windows 11 | 3.12 | Unit, integration, UI |
| macOS 14 | 3.12 | Unit, integration, UI |

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `TELEGRAM_TOKEN` | Bot authentication | No |
| `GOOGLE_SERVICE_ACCOUNT_FILE` | Google API credentials | No |
| `DATABASE_URL` | Database connection | No |
| `CALLBACK_SECRET_KEY` | HMAC validation | No |
| `LOG_LEVEL` | Logging level | No |
| `LOG_FILE` | Log file path | No |

## Monitoring

### Application Metrics

- Processing time per file
- Memory usage
- CPU utilization
- Error rates
- User session duration

### Logging

- Use `loguru` for structured logging
- Log to file and console
- Rotate logs to prevent disk fill
- Include timestamps and log levels
