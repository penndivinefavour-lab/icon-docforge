# ICON DocForge v1.4 — Production APK Transformation Plan

## Executive Summary

Transform ICON DocForge from a developer-grade Termux tool into a polished, trustworthy, production-quality public Android application. The core engine remains unchanged; we build a proper Android wrapper with a refined UI, safe file handling, and accurate capability reporting.

---

## Phase 1: Foundation (Checkpoint)

- [x] Audit existing codebase
- [ ] Create clean Git checkpoint from v1.3.0
- [ ] Branch: `v1.4-production-apk`
- [ ] Verify all existing tests pass

---

## Phase 2: Capability Audit & Matrix

### Android APK vs Termux vs Web/PWA

**Android APK (Standalone):**
- Python runs via Chaquopy or Brython? → **No** — needs Capacitor + WebView + local server
- File picker: Android Storage Access Framework ✓
- HTTP API: localhost binding ✓
- All Python converters available if bundled correctly

**Termux (Full):**
- Complete CLI access
- All engines (pandoc, poppler, etc.)
- OCR potential (when tesseract installed)

**Web/PWA:**
- Limited to what browser can do
- No direct file system access
- Requires user to start server manually

### Strict Capability Matrix

| Conversion | APK | Termux | Web | Notes |
|------------|-----|--------|-----|-------|
| DOCX → PDF | ✓ | ✓ | ✓ | pandoc+weasyprint |
| PDF → DOCX | ✓* | ✓ | ✗ | Reconstructed quality |
| Images → PDF | ✓ | ✓ | ✓ | Multi-image supported |
| PDF Merge | ✓ | ✓ | ✓ | Using pypdf2 |
| PDF Split | ✓ | ✓ | ✓ | |
| PDF Reorder | ✓ | ✓ | ✓ | |
| PDF Rotate | ✓ | ✓ | ✓ | |
| PDF Compress | ✓ | ✓ | ✓ | |
| PDF → Images | ✓ | ✓ | ✓ | PNG/JPEG/WebP |
| PPTX → PDF | ✓ | ✓ | ✓ | python-pptx+reportlab |
| XLSX → PDF | ✓ | ✓ | ✓ | openpyxl+reportlab |
| CSV ↔ XLSX | ✓ | ✓ | ✓ | |
| Markdown → PDF | ✓ | ✓ | ✓ | pandoc |
| PDF → DOCX (OCR) | ⚠️ | ✓ | ✗ | Requires Tesseract |

✓ = Fully supported
✓* = Supported with fidelity warning
⚠️ = Available only with optional engine

---

## Phase 3: Android Wrapper Architecture

### Technology Stack
- **Framework**: Capacitor 6.x (modern, stable)
- **UI**: Custom PWA-style with brand design system
- **Communication**: Local HTTP API (127.0.0.1:8765)
- **File Handling**: Android SAF + Capacitor Filesystem plugin

### Directory Structure
```
android/                    # Android project root
├── app/
│   ├── src/main/
│   │   ├── java/com/iconstudios/docforge/
│   │   │   ├── MainActivity.kt      # Main activity
│   │   │   └── DocForgeApp.kt       # Application class
│   │   ├── res/
│   │   │   ├── drawable/            # Icons, drawables
│   │   │   ├── mipmap-anydpi-v26/   # Adaptive icons
│   │   │   ├── values/              # Colors, strings, themes
│   │   │   └── xml/                 # File paths, permissions
│   │   ├── AndroidManifest.xml
│   │   └── assets/www/            # Web assets
│   └── build.gradle.kts
├── capacitor.settings.gradle
└── gradle.properties
```

### Key Components
1. **MainActivity**: Launches WebView, handles file picker intents
2. **WebViewBridge**: JavaScript bridge for native calls
3. **LocalServerService**: Runs Python HTTP API in background
4. **FileProvider**: Secure file sharing between app and system

---

## Phase 4: UI/UX Redesign

### Design System
- **Primary Color**: #6b21a8 (ICON Studios Purple)
- **Secondary**: #f5c518 (Gold accent)
- **Background**: #f4f4f8 (Light gray)
- **Surface**: #ffffff (White cards)
- **Text**: #1f2128 (Dark navy)
- **Font**: Poppins (system fallback)

### Screens
1. **Home**: Grid of conversion tools, recent history
2. **Tool Detail**: File picker, options, progress
3. **Result**: Output file info, actions (open/share/save)
4. **Settings**: Diagnostics, about, privacy info

### UX Principles
- Clear privacy statement on first launch
- No account required
- Explicit unsupported state (grayed out, not broken)
- Fidelity warnings for reconstructed conversions
- Proper error messages (no stack traces)

---

## Phase 5: Security Hardening

### Local HTTP API
- Bind to 127.0.0.1 only (already implemented)
- Input validation for all paths
- Size limits enforced
- No shell injection (use argument arrays)

### File Handling
- Use SAF for user files
- Process in app's temp directory
- Clean up after completion
- Never access arbitrary filesystem paths

### Network
- No external API calls during conversion
- No telemetry or analytics
- No crash reporting to third parties
- Explicit offline-first design

---

## Phase 6: Testing & QA

### Test Coverage Target
- 100+ unit tests (existing + new)
- Real-device testing on Pixel 4a
- Offline mode verification
- Error handling edge cases
- Performance benchmarks

### Test Categories
1. Unit tests: Engine converters, utility functions
2. Integration tests: Full conversion workflows
3. UI tests: Navigation, file picker, result display
4. Security tests: Path traversal, injection attempts
5. Performance tests: Large file handling, memory usage

---

## Phase 7: Build & Release

### GitHub Actions
- Automated test suite
- APK build (debug + release)
- SHA-256 checksum generation
- GitHub Release creation
- Artifact upload

### Signing
- Generate keystore securely (not in repo)
- Use GitHub Secrets for signing keys
- Verify APK signature post-build
- Document signing setup

### Distribution
- GitHub Releases as primary channel
- Direct APK download
- Version tags (v1.4.0, v1.4.1, etc.)
- Release notes with capability matrix

---

## Phase 8: Documentation

### Required Files
- README.md: Updated with APK focus
- INSTALL_ANDROID.md: Installation guide
- PRODUCT.md: Product description
- PRIVACY.md: Privacy policy
- SECURITY.md: Security architecture
- CHANGELOG.md: Version history
- RELEASE_CHECKLIST.md: Pre-release checklist
- SUPPORT.md: User support info

---

## Timeline Estimate

| Phase | Duration | Status |
|-------|----------|--------|
| 1. Foundation | 2 hours | In Progress |
| 2. Capability Audit | 1 hour | Pending |
| 3. Android Wrapper | 4 hours | Pending |
| 4. UI/UX Redesign | 3 hours | Pending |
| 5. Security Hardening | 2 hours | Pending |
| 6. Testing & QA | 3 hours | Pending |
| 7. Build & Release | 2 hours | Pending |
| 8. Documentation | 2 hours | Pending |
| **Total** | **~19 hours** | |

---

## Success Criteria

- [ ] APK installs and launches successfully
- [ ] All supported conversions work offline
- [ ] Unsupported features clearly communicated
- [ ] No technical errors shown to users
- [ ] File picker works with Android SAF
- [ ] Results can be opened/shared
- [ ] Temporary files cleaned up properly
- [ ] GitHub Release contains signed APK
- [ ] Documentation is complete and accurate
- [ ] 100+ tests passing

---

*Plan created: September 2026*
*Author: Divine Favour · ICON Studios*
