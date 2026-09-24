# Architecture Document

## Overview

ICON DocForge is a **local-first document conversion platform** built on three pillars:

1. **Python Conversion Engine** — Core logic using open-source libraries
2. **Local HTTP Server** — Lightweight API bridge between web UI and engine
3. **Web Interface** — Vanilla HTML/CSS/JS frontend served locally or via Capacitor

The entire system runs offline. No data ever leaves the device during conversion.

---

## Design Decisions

### Why Python Engine?

- **Maturity**: Libraries like `pdf2docx`, `python-docx`, `python-pptx`, and `openpyxl` are well-maintained and widely used.
- **Android compatibility**: Python runs in Termux and can be bundled via Capacitor's Android WebView.
- **Performance**: Native Python bindings for PDF/image processing are faster than JavaScript alternatives.

### Why Local HTTP Server?

- **Separation of concerns**: Web UI handles presentation; Python handles computation.
- **Cross-platform**: Same server works in Termux, Android, desktop, and CI/CD.
- **Simplicity**: Flask-based server adds minimal overhead (~10ms latency locally).
- **Debuggability**: HTTP endpoints are easily testable with `curl`.

### Why Capacitor for Android?

- **Proven pattern**: Reuses the same architecture that powers ICON QuickTools successfully.
- **Native WebView**: Uses Android's WebView with full JavaScript support.
- **Plugin ecosystem**: Access to share, clipboard, file system via Capacitor plugins.
- **Single codebase**: Web UI works identically across Termux, APK, and GitHub Pages.

---

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                         │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  Web UI (HTML/CSS/JS)                                │    │
│  │  ├── Home screen: format selection + file upload     │    │
│  │  ├── Progress indicator + status messages            │    │
│  │  ├── Results display + download button               │    │
│  │  └── History/log panel                               │    │
│  └──────────────────────┬───────────────────────────────┘    │
│                         │                                    │
│              ┌──────────▼──────────┐                          │
│              │  Local HTTP Server  │                          │
│              │  (Flask, :8080)     │                          │
│              │                     │                          │
│              │  POST /convert      │                          │
│              │  GET  /status/:id   │                          │
│              │  GET  /download/:id │                          │
│              │  GET  /formats      │                          │
│              └──────────┬──────────┘                          │
└─────────────────────────┼────────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────────┐
│                     CONVERSION ENGINE                          │
│                                                               │
│  ┌──────────────────────────────────────────────────────┐    │
│  │  python-docx                                          │    │
│  │  ├── DOCX → PDF (via pandoc if available)            │    │
│  │  ├── DOCX → Images (render pages)                    │    │
│  │  └── DOCX editing (text/style changes)               │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │  pdf2docx                                             │    │
│  │  ├── PDF → DOCX (reconstruction)                     │    │
│  │  ├── PDF → Images (page-by-page render)              │    │
│  │  └── PDF metadata extraction                         │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │  python-pptx                                          │    │
│  │  ├── PPTX → PDF                                      │    │
│  │  ├── PPTX → Images (slide render)                    │    │
│  │  └── PPTX editing (text/bullet changes)              │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │  openpyxl                                             │    │
│  │  ├── XLSX → CSV                                      │    │
│  │  ├── CSV → XLSX                                      │    │
│  │  ├── XLSX → PDF                                      │    │
│  │  └── Excel data manipulation                         │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │  PyMuPDF (fitz)                                       │    │
│  │  ├── PDF rendering (page images)                     │    │
│  │  ├── PDF metadata extraction                         │    │
│  │  ├── PDF page extraction                             │    │
│  │  └── Image → PDF conversion                          │    │
│  ├──────────────────────────────────────────────────────┤    │
│  │  Pillow                                               │    │
│  │  ├── Image format conversion (PNG/JPG/WebP)          │    │
│  │  ├── Image resize/crop/rotate                        │    │
│  │  └── Image compression                               │    │
│  └──────────────────────────────────────────────────────┘    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

---

## Module System

Each converter is a self-contained module:

```python
class Converter:
    def __init__(self):
        self.name = "base"
        self.supported_from = []
        self.supported_to = []
    
    def convert(self, input_path: str, output_path: str, **kwargs) -> dict:
        """Perform conversion. Returns status dict."""
        raise NotImplementedError
    
    def validate(self, input_path: str) -> bool:
        """Validate input file before conversion."""
        raise NotImplementedError
```

Modules register themselves with the engine registry. New converters can be added without modifying the HTTP server or web UI.

---

## State Management

- **Conversion jobs** are tracked in memory with UUID identifiers
- **Job status** progresses: `queued` → `processing` → `completed` / `failed`
- **Results** are stored temporarily and cleaned up after download
- **No persistent database** — all state is ephemeral per session

---

## File Flow

```
User uploads file → Saved to /tmp/docforge/{uuid}/input
                  → Converter processes file
                  → Output saved to /tmp/docforge/{uuid}/output/{name}.{ext}
                  → Download link generated
                  → File cleaned up after TTL expiry
```

---

## Performance Considerations

- **Synchronous processing**: Each conversion runs sequentially in a single thread (safe for the file sizes we expect).
- **Memory management**: Large files (>50MB) are processed in chunks where possible.
- **Timeout**: Conversions have a 5-minute timeout to prevent hangs.

---

## Security Considerations

- **Local-only server**: Binds to `127.0.0.1`, not `0.0.0.0`
- **File validation**: Input files are checked for magic bytes and size limits
- **Sandboxed temp directory**: `/tmp/docforge/` with restricted permissions
- **No external network calls**: Conversion engine has zero outbound connections

See [SECURITY.md](SECURITY.md) for full details.

---

## Future Architecture Additions

- **Async processing**: Use `asyncio` for parallel batch conversions
- **OCR support**: Integrate Tesseract for image-only PDFs
- **Plugin system**: Allow third-party converter modules
- **Distributed mode**: Support remote conversion server (trusted network only)
