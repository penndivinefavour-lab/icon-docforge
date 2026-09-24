# CHANGELOG — ICON DocForge

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Production Android APK infrastructure (Capacitor 6.x)
- Redesigned UI with professional design system
- Security hardening (localhost-only API, path validation, subprocess safety)
- Comprehensive documentation (Security, Privacy, Support guides)
- Accurate capability reporting (shows only available features)
- File picker integration with Android SAF
- Settings/diagnostics screen
- Error handling with user-friendly messages

### Security
- Localhost binding enforced (127.0.0.1:8765)
- Network security config blocks cleartext traffic
- Path traversal prevention in all file operations
- Subprocess safety (argument arrays, no shell interpolation)
- Minimal Android permissions (INTERNET + READ_STORAGE only)
- Automatic temp file cleanup after conversion
- No external network calls during conversion

### Capabilities Matrix

| Feature | APK | Termux | Web |
|---------|-----|--------|-----|
| Images → PDF | ✓ | ✓ | ✓ |
| PDF Merge | ✓ | ✓ | ✗ |
| PDF Split | ✓ | ✓ | ✗ |
| DOCX → PDF | ⚠️ | ✓ | ✓ |
| CSV ↔ XLSX | ✗ | ✓ | ✗ |
| PPTX → PDF | ✗ | ✓ | ✗ |
| PDF → Images | ✗ | ✓ | ✗ |
| OCR | ⚠️ | ⚠️ | ✗ |

✓ = Fully supported
⚠️ = Partially supported / requires additional packages
✗ = Not available

### Known Limitations
- Maximum file size: 50MB
- Some converters require Python packages not bundled in base APK
- OCR engine (Tesseract) requires separate installation
- APK build requires CI/CD environment (Android SDK)

### Documentation Added
- SECURITY.md - Complete security architecture
- PRIVACY.md - Zero-data collection policy
- SUPPORT.md - User support and FAQ
- INSTALL_ANDROID.md - Installation guide
- APK_BUILD_GUIDE.md - Build instructions
- PRODUCT_IDENTITY.md - Design system guidelines
- PRODUCTION_COMPLETION_REPORT.md - Implementation summary

---

## [v1.4.0] - 2026-09-24

### Added
- Complete Android APK project structure (android-apk/)
- Production-quality web UI redesign
- MainActivity.kt with file picker integration
- Network security configuration
- Gradle build configuration
- Capacitor configuration for Android
- Package.json for Android dependencies

### Changed
- Updated version to 1.4.0
- Redesigned web/index.html with clean UI
- Rewrote web/js/app.js with proper navigation
- Added tool modules registry (web/js/tools/main.js)
- Updated documentation throughout

### Security Improvements
- Enforced localhost-only API binding
- Added network security config
- Implemented input validation in all file operations
- Added file size limits (50MB max)
- Configured ProGuard for release builds

### Testing
- 73 unit tests passing (55 v1.2 + 18 new OCR tests)
- Security audit completed
- Privacy compliance verified

---

## [v1.3.0] - 2026-09-24

### Added
- OCR pipeline infrastructure (engine/ocr_engine.py, ocr_pipeline.py)
- PDF to image converter (pdf_to_image.py)
- Tesseract/Dummy engine abstraction
- CLI commands: `iconconvert ocr`, `iconconvert ocr-status`
- 18 OCR unit tests
- 10 OCR test fixtures (English, French, mixed, rotated, low-res, etc.)
- OCR_ENGINE_RESEARCH.md documenting all investigated engines

### Notes
- OCR recognition deferred due to unavailable engine binary
- Pipeline ready for activation when Tesseract installed
- All v1.2 functionality preserved

---

## [v1.2.0] - 2026-09-24

### Added
- Office document conversion expansion
- 16 converter modules total
- PPTX → PDF, XLSX → PDF, ODT conversions
- CLI extensions for new converters
- Office conversion matrix documentation
- Improved error handling in converters

### Status
- 55/55 tests passing
- All core conversions operational

---

## [v1.1.0] - 2026-09-23

### Added
- Basic document conversion engines
- HTTP API server (http_api.py)
- PWA web interface
- Initial Android wrapper concept
- README and documentation

---

## [v1.0.0] - 2026-09-22

### Added
- Initial project scaffolding
- MIT License
- GitHub repository setup
- Basic documentation

---

## Download & Installation

### Android APK
Download from GitHub Releases:
https://github.com/penndivinefavour-lab/icon-docforge/releases

See [INSTALL_ANDROID.md](INSTALL_ANDROID.md) for details.

### Termux
```bash
pkg update && pkg upgrade
pkg install python python-pip pandoc poppler
git clone https://github.com/penndivinefavour-lab/icon-docforge.git
cd icon-docforge
pip install -r requirements.txt
python3 engine/cli.py --help
```

## Contributing

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before submitting PRs.

## License

MIT License - see [LICENSE](LICENSE) for details.

## Support

- GitHub Issues: https://github.com/penndivinefavour-lab/icon-docforge/issues
- Email: iconstudiosyde@gmail.com

---

*ICON DocForge by ICON Studios · Yaoundé, Cameroon*
