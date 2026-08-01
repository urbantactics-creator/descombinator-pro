---
name: git-workflow-manager
description: >-
  Git workflow management, branching strategy, commit conventions, pull request
  process, and repository maintenance for the Descombinator Pro project.
license: MIT
metadata:
  category: devops
  project: descombinator-pro
---

# Git Workflow Manager

## Responsibilities

- Define and enforce Git workflow standards
- Manage branching strategy
- Enforce commit message conventions
- Review and merge pull requests
- Maintain repository health

## Branching Strategy

### Git Flow Variant

| Branch | Purpose | Protection |
|--------|---------|-----------|
| `master` | Production releases | ✅ Protected |
| `develop` | Development integration | ✅ Protected |
| `feature/*` | New features | ❌ |
| `bugfix/*` | Bug fixes | ❌ |
| `hotfix/*` | Production fixes | ❌ |

### Branch Naming

```
feature/vocal-separation
feature/multi-instrument
bugfix/audio-loading-crash
hotfix/critical-memory-leak
```

## Commit Conventions

### Format

```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types

| Type | Purpose |
|------|---------|
| `feat` | New feature |
| `fix` | Bug fix |
| `docs` | Documentation changes |
| `style` | Code formatting, whitespace |
| `refactor` | Code refactoring |
| `perf` | Performance improvements |
| `test` | Test additions or fixes |
| `build` | Build system changes |
| `ci` | CI configuration changes |
| `chore` | Maintenance tasks |
| `revert` | Revert a previous commit |

### Examples

```
feat(separation): add Demucs v4 vocal separation

Implement the core separation pipeline using Demucs htdemucs_ft model.
Supports MP3, WAV, and FLAC input formats.

Closes #123
```

## Pull Request Process

1. Create feature branch from `develop`
2. Implement changes with tests
3. Run full test suite
4. Create PR with description
5. Assign reviewers
6. Address feedback
7. Merge to `develop`

## Repository Maintenance

- Regular garbage collection
- Clean up stale branches
- Update `.gitignore` as needed
- Maintain `AGENTS.md` and skill documentation
