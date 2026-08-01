---
name: packaging-distribution-engineer
description: >-
  Application packaging, installer creation, code signing, release management,
  and distribution for the Descombinator Pro desktop application.
license: MIT
metadata:
  category: devops
  project: descombinator-pro
---

# Packaging & Distribution Engineer

## Responsibilities

- Package the application for Windows, macOS, and Linux
- Create installers and distributable packages
- Implement code signing for security
- Manage release versioning and changelogs
- Automate release builds

## Packaging Tools

| Platform | Tool | Output |
|----------|------|--------|
| Windows | PyInstaller + NSIS | .exe installer |
| macOS | PyInstaller + pkgbuild | .dmg, .pkg |
| Linux | PyInstaller + AppImage | .AppImage, .deb, .rpm |

## PyInstaller Configuration

### spec File

```python
# descombinator.spec
a = Analysis(
    ['main.py'],
    pathex=['/home/mint/Desktop/descombinator'],
    binaries=[],
    datas=[
        ('app/resources/*', 'app/resources'),
        ('engine/inference/weights/*', 'engine/inference/weights'),
    ],
    hiddenimports=['PySide6', 'torch', 'demucs'],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
)
```

### Build Commands

```bash
# Windows
pyinstaller --onefile --windowed descombinator.spec

# macOS
pyinstaller --onefile --windowed --osx-bundle-identifier=com.descombinator.pro descombinator.spec

# Linux
pyinstaller --onefile --windowed descombinator.spec
```

## Code Signing

### Windows

- Use `signtool` to sign executables
- Obtain code signing certificate
- Sign all binaries and installers

### macOS

- Use `codesign` to sign the application bundle
- Notarize with Apple's notary service
- Staple the notarization ticket

## Release Process

### Versioning

- Use semantic versioning (MAJOR.MINOR.PATCH)
- Tag releases in Git
- Generate changelog from commit messages

### Release Checklist

1. Run full test suite
2. Build for all platforms
3. Code sign all binaries
4. Upload to GitHub Releases
5. Update documentation
6. Announce release

## Distribution Channels

| Channel | Platform |
|---------|----------|
| GitHub Releases | All |
| Microsoft Store | Windows |
| Mac App Store | macOS |
| Flathub | Linux |
| Website | All |
