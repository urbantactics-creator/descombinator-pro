# License Compliance

This document covers the licensing of Descombinator Pro's code, dependencies, and AI model weights.

## Code License

The Descombinator Pro source code is licensed under the **MIT License**.

```
MIT License

Copyright (c) 2026 Descombinator Pro

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Dependency Licenses

### Core Dependencies

| Package | License | Notes |
|---------|---------|-------|
| `torch` | BSD-3-Clause | PyTorch — BSD license |
| `torchaudio` | BSD-3-Clause | PyTorch audio — BSD license |
| `demucs` | MIT | Facebook AI Research — MIT license |
| `openunmix` | MIT | — MIT license |
| `librosa` | ISC | — ISC license |
| `soundfile` | BSD-3-Clause | — BSD license |
| `audioread` | MIT | — MIT license |
| `resampy` | MIT | — MIT license |
| `numpy` | BSD-3-Clause | — BSD license |
| `scipy` | BSD-3-Clause | — BSD license |
| `mutagen` | GPL-3.0-or-later | **Note:** Mutagen is GPL-3.0. If you distribute a binary that includes Mutagen, you must also provide the source code of Mutagen and any modifications. |
| `PySide6` | LGPL-3.0-only | Qt for Python — LGPL v3. See [Qt Licensing](https://www.qt.io/licensing) for details. |
| `pyqtgraph` | MIT | — MIT license |
| `aiofiles` | MIT | — MIT license |
| `pydantic` | MIT | — MIT license |
| `loguru` | MIT | — MIT license |
| `psutil` | MIT | — MIT license |
| `rich` | MIT | — MIT license |
| `python-dotenv` | BSD-3-Clause | — BSD license |
| `PyYAML` | MIT | — MIT license |

### Dev Dependencies

| Package | License | Notes |
|---------|---------|-------|
| `pytest` | MIT | — MIT license |
| `pytest-asyncio` | Apache-2.0 | — Apache 2.0 license |
| `pytest-qt` | GPL-2.0-or-later | **Note:** GPL-2.0. Only used for testing, not distributed with the application. |
| `pytest-cov` | MIT | — MIT license |
| `pytest-benchmark` | Apache-2.0 | — Apache 2.0 license |
| `ruff` | MIT | — MIT license |
| `mypy` | MIT | — MIT license |
| `pre-commit` | MIT | — MIT license |
| `pyinstaller` | GPL-2.0-with-exception | **Note:** PyInstaller is GPL-2.0 with a special exception. See [PyInstaller License](https://github.com/pyinstaller/pyinstaller/blob/master/LICENSE.txt). |
| `memory-profiler` | BSD-3-Clause | — BSD license |
| `py-spy` | MIT | — MIT license |
| `snakeviz` | MIT | — MIT license |

## AI Model Weights

### Demucs Models

Demucs models are distributed under the **MIT License** (same as the Demucs library).

- `htdemucs_ft` — Fine-tuned Hybrid Task-Cascaded Demucs
- `mdx_extra` — MDX-Net extra model

Source: [https://github.com/facebookresearch/demucs](https://github.com/facebookresearch/demucs)

### Open-Unmix Models

Open-Unmix models are distributed under the **MIT License**.

- `umxhq` — Open-Unmix HQ model

Source: [https://github.com/sigsep/open-unmix-pytorch](https://github.com/sigsep/open-unmix-pytorch)

## License Compliance Checklist

Before distributing a public release, verify:

- [ ] All dependency licenses are compatible with MIT
- [ ] Mutagen (GPL-3.0) source code is available if distributing binaries
- [ ] PySide6 (LGPL-3.0) dynamic linking is used (not static linking)
- [ ] PyInstaller (GPL-2.0 with exception) is used only for building, not distributed
- [ ] Model weights are properly attributed to their original sources
- [ ] LICENSE file is included in the distribution
- [ ] Third-party license notices are included in the distribution

## Third-Party License Notices

When distributing the application, include the following:

1. **LICENSE** — The MIT license for Descombinator Pro
2. **NOTICE** — Attribution for third-party libraries and model weights
3. **THIRD-PARTY-LICENSES** — Full text of all third-party licenses

## Generating License Reports

Use `pip-licenses` to generate a license report:

```bash
pip install pip-licenses
pip-licenses --format=markdown --with-urls > docs/license-compliance/third-party-licenses.md
```

## Questions

If you have questions about licensing, please open an issue on GitHub.
