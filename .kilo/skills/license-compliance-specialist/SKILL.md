---
name: license-compliance-specialist
description: >-
  License compliance auditing, dependency license tracking, license compatibility
  analysis, and open source compliance for the Descombinator Pro project.
license: MIT
metadata:
  category: legal
  project: descombinator-pro
---

# License Compliance Specialist

## Responsibilities

- Audit all dependencies for license compliance
- Track and document license information
- Ensure license compatibility
- Handle license headers in source files
- Prepare for open source release

## License Policy

### Allowed Licenses

| License | Usage |
|---------|-------|
| MIT | ✅ Full use, modification, distribution |
| BSD 2-Clause | ✅ Full use, modification, distribution |
| BSD 3-Clause | ✅ Full use, modification, distribution |
| Apache 2.0 | ✅ Full use, modification, distribution |
| LGPL | ✅ Dynamic linking only |
| GPL | ⚠️ Review required |
| Proprietary | ❌ No use |

### Prohibited Licenses

- AGPL (viral, requires network source disclosure)
- SSPL (proprietary-like restrictions)
- Custom licenses with unclear terms

## Dependency License Audit

### Key Dependencies

| Package | License | Notes |
|---------|---------|-------|
| torch | BSD-3-Clause | ✅ |
| demucs | MIT | ✅ |
| PySide6 | LGPL-3.0 | ✅ Dynamic linking |
| librosa | ISC | ✅ |
| numpy | BSD-3-Clause | ✅ |
| scipy | BSD-3-Clause | ✅ |
| soundfile | BSD-3-Clause | ✅ |
| mutagen | GPL-3.0 | ⚠️ Review for distribution |
| openunmix | MIT | ✅ |
| pyinstaller | GPL-2.0 | ⚠️ Review for distribution |

## License Headers

### Source Files

```python
# SPDX-License-Identifier: MIT
# Copyright (c) 2026 Descombinator Pro Contributors
```

### License File

- Include `LICENSE` file in project root
- Include `LICENSES/` directory with third-party licenses
- Document license compliance in `docs/license-compliance.md`

## Model Licenses

### AI Models

| Model | License | Notes |
|-------|---------|-------|
| Demucs | MIT | ✅ |
| Open-Unmix | MIT | ✅ |
| Future models | Check individually | Document before use |

## Compliance Process

1. Audit all dependencies before adding
2. Document license in `docs/licenses/`
3. Include license text in distribution
4. Review before each release
5. Maintain license inventory
