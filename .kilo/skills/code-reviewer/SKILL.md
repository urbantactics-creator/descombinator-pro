---
name: code-reviewer
description: >-
  Code review standards, review checklist, code quality guidelines, and
  peer review process for the Descombinator Pro project.
license: MIT
metadata:
  category: quality
  project: descombinator-pro
---

# Code Reviewer

## Responsibilities

- Review all code changes before merging
- Enforce code quality standards
- Ensure adherence to project architecture
- Verify test coverage for new code
- Provide constructive feedback

## Review Checklist

### Architecture

- [ ] Code follows the module structure (`app/`, `engine/`)
- [ ] Dependencies flow in the correct direction (no circular imports)
- [ ] New code doesn't violate layer boundaries
- [ ] State management follows established patterns

### Code Quality

- [ ] Type hints on all function signatures
- [ ] Docstrings on public methods
- [ ] No unused imports or variables
- [ ] Functions are small and focused (single responsibility)
- [ ] Error handling is appropriate and consistent
- [ ] Logging uses `loguru` with proper context

### Async Patterns

- [ ] All I/O operations use `async def`
- [ ] No blocking calls in async functions
- [ ] Proper use of `asyncio` primitives
- [ ] No `asyncio.to_thread` for Google API calls (per architecture rules)

### Testing

- [ ] New code has unit tests
- [ ] Edge cases are covered
- [ ] Mocks are used for external dependencies
- [ ] Test names are descriptive

### Security

- [ ] No hardcoded secrets or credentials
- [ ] File paths are validated
- [ ] User input is sanitized
- [ ] No exposure of internal errors to users

### Performance

- [ ] No unnecessary file I/O
- [ ] Memory usage is reasonable
- [ ] No blocking the UI thread
- [ ] Efficient algorithms used

## Review Process

1. Author creates pull request with description
2. Assign at least one reviewer
3. Reviewer checks all checklist items
4. Address feedback with additional commits
5. Approve and merge after all checks pass
