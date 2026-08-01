---
name: dependency-manager
description: >-
  Python dependency management, virtual environment setup, package versioning,
  and dependency security auditing for the Descombinator Pro project.
license: MIT
metadata:
  category: devops
  project: descombinator-pro
---

# Dependency Manager

## Responsibilities

- Manage Python dependencies via `requirements.txt` and `pyproject.toml`
- Set up and maintain virtual environments
- Pin dependency versions for reproducibility
- Audit dependencies for security vulnerabilities
- Handle dependency conflicts and upgrades

## Dependency Management

### requirements.txt

- Pin exact versions for production dependencies
- Use `>=` for minimum version requirements
- Group dependencies by category with comments
- Keep file sorted alphabetically within groups

### pyproject.toml

- Define project metadata (name, version, description)
- Configure build system (setuptools)
- Define entry points and scripts
- Set Python version requirement (>=3.12)

## Virtual Environment

### Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Auto-activation

- `.envrc` for direnv integration
- `activate.sh` for manual activation
- Add to `.bashrc` for shell auto-activation

## Version Pinning Strategy

| Dependency | Strategy | Reason |
|------------|----------|--------|
| torch | Pin major.minor | Large, breaking changes |
| demucs | Pin major | API stability |
| PySide6 | Pin major.minor | UI compatibility |
| librosa | Pin major | API changes |
| numpy | Pin major | Breaking changes |

## Security Auditing

### Tools

- `pip-audit` — Check for known vulnerabilities
- `safety` — Scan for insecure packages
- `bandit` — Static analysis for security issues

### Process

1. Run `pip-audit` weekly
2. Review and update dependencies monthly
3. Test after each dependency update
4. Document security advisories

## Dependency Conflicts

### Resolution

- Use `pip-tools` for lock file generation
- Resolve conflicts with `pip check`
- Test in clean virtual environment
- Document resolution in `docs/dependencies.md`
