# Development Roadmap

## Overview

ICON DocForge follows an iterative development approach. This roadmap outlines planned features, improvements, and milestones.

---

## Version 1.0.0 (Current — September 2026) ✅

### Completed
- ✅ Core conversion engine with Python libraries
- ✅ PDF→DOCX reconstruction via pdf2docx
- ✅ DOCX↔PDF, PPTX↔PDF, XLSX↔CSV conversions
- ✅ Image format conversion (PNG/JPG/WebP/BMP/TIFF)
- ✅ Local HTTP server with web UI
- ✅ CLI mode for Termux
- ✅ Android APK wrapper via Capacitor
- ✅ GitHub Actions CI/CD pipeline
- ✅ Test suite with fixture files
- ✅ Documentation (README, Architecture, Formats, Privacy, Security)

---

## Version 1.1.0 (Planned — Q4 2026)

### PDF Enhancement
- [ ] **OCR integration** — Add Tesseract OCR for image-only PDFs
- [ ] **PDF password support** — Decrypt password-protected PDFs
- [ ] **PDF metadata editing** — Modify title, author, subject
- [ ] **PDF merge/split** — Combine or split PDF files
- [ ] **PDF annotations** — Extract and preserve annotations

### DOCX Enhancement
- [ ] **DOCX template support** — Fill in mail-merge style templates
- [ ] **DOCX table formatting** — Preserve borders, shading, column widths
- [ ] **DOCX styles** — Map PDF styles to Word styles

### XLSX Enhancement
- [ ] **Excel formula preservation** — Preserve formulas during XLSX↔XLSX
- [ ] **Multi-sheet export** — Export each sheet to separate file
- [ ] **Chart preservation** — Extract chart data from XLSX

### UI Enhancement
- [ ] **Dark mode** — Toggle dark/light theme
- [ ] **Keyboard shortcuts** — Ctrl+K for conversion, Ctrl+D for download
- [ ] **Drag and drop** — Drag files onto the web UI
- [ ] **Conversion history** — View recent conversions locally
- [ ] **Progress bar** — Visual progress indicator for long conversions

---

## Version 2.0.0 (Planned — Q1 2027)

### OCR & Advanced Features
- [ ] **Full OCR pipeline** — Tesseract integration with language selection
- [ ] **OCR confidence scores** — Show quality of text extraction
- [ ] **Handwriting recognition** (research phase)

### Performance & Scale
- [ ] **Async processing** — Use `asyncio` for parallel batch conversions
- [ ] **Streaming conversion** — Process large files in chunks
- [ ] **Compression support** — Handle ZIP-compressed formats

### Plugin System
- [ ] **Custom converter API** — Allow third-party converter modules
- [ ] **Plugin marketplace** — Browse and install community converters
- [ ] **Converter SDK** — Documentation for building custom converters

### Collaboration
- [ ] **Shareable links** — Generate time-limited links to converted files (self-hosted)
- [ ] **Team workspace** — Multi-user document processing (trusted network only)

---

## Platform Roadmap

### Web Progressive App (PWA)
- [ ] Service worker for offline-first experience
- [ ] Push notifications for batch conversion completion
- [ ] Web Share API for sharing converted files
- [ ] Background sync for queued conversions

### Desktop Application
- [ ] Electron wrapper for Windows/macOS/Linux
- [ ] Native file system integration
- [ ] System tray integration

### iOS/iPadOS (Research)
- [ ] Swift-based conversion engine
- [ ] Native document picker integration
- [ ] iCloud Drive support

---

## Community & Ecosystem

- [ ] **Documentation website** — Static site with search
- [ ] **Video tutorials** — Walkthroughs for common use cases
- [ ] **Contributor guide** — Streamlined onboarding for new developers
- [ ] **Translation support** — i18n for multiple languages (French, Spanish, Hindi)

---

## Technical Debt

### High Priority
- [ ] Replace `pdf2docx` with more robust extraction pipeline if quality doesn't meet expectations
- [ ] Add proper error classification (transient vs permanent failures)
- [ ] Implement file validation against known malformed formats

### Medium Priority
- [ ] Add type hints to all Python modules
- [ ] Implement proper logging configuration (logrotate, structured logs)
- [ ] Add performance benchmarks and profiling

### Low Priority
- [ ] Containerize the engine for Docker deployment
- [ ] Add health check endpoints for monitoring
- [ ] Implement circuit breaker pattern for failed conversions

---

## Release Schedule

| Version | Target | Focus |
|---------|--------|-------|
| 1.0.0 | Sep 2026 | Core engine, web UI, Android APK |
| 1.1.0 | Dec 2026 | OCR, UI improvements, PDF/DOCX enhancements |
| 2.0.0 | Mar 2027 | Async, plugins, collaboration |

---

## Contributing

See [TESTING.md](TESTING.md) for test procedures and [CONTRIBUTING.md](CONTRIBUTING.md) (planned) for contribution guidelines.

---

## Vision

ICON DocForge aims to be the **universal document converter** — a single tool that handles any format, runs anywhere, and never compromises your privacy.
