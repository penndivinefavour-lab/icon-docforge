# ICON DocForge v1.3 — OCR & Scanned Document Processing

## Release Summary

v1.3 adds **offline OCR infrastructure** to ICON DocForge, enabling scanned document processing on Android/Termux without cloud dependencies. Due to environment constraints, the OCR recognition engine is currently unavailable but the complete pipeline architecture is in place for immediate activation when Tesseract becomes installable.

---

## What's New in v1.3

### Core Features

1. **OCR Engine Abstraction Layer** (`engine/ocr_engine.py`)
   - Pluggable engine interface supporting Tesseract and future engines
   - Graceful degradation when no engine is available
   - Language pack support for English, French, and 6+ additional languages
   - Confidence scoring and word-level confidence extraction
   - Three preprocessing profiles: FAST, BALANCED, QUALITY

2. **PDF to Image Converter** (`engine/converters/pdf_to_image.py`)
   - Renders PDF pages to PNG/JPEG/WebP images
   - Configurable DPI (72-300+)
   - Page range selection
   - Uses pypdfium2 (already available from v1.2)

3. **OCR Pipeline** (`engine/converters/ocr_pipeline.py`)
   - Multi-stage pipeline: validate → preprocess → recognize → postprocess
   - Auto mode: detects text-heavy pages and preserves selectable text
   - Force mode: OCRs all pages regardless
   - Supports image inputs (PNG, JPG, WebP, BMP, TIFF) and PDF input
   - Output formats: plain text, JSON, HTML

4. **CLI Commands**
   ```bash
   iconconvert ocr <input> --language fra --profile quality --format txt
   iconconvert ocr-status
   ```

5. **Engine Diagnostics**
   - `iconconvert ocr-status` shows available engines and recommendations
   - Clear installation instructions when engine is missing
   - Compatibility checks for ARM64/Android environment

### Test Coverage

- **10 OCR test fixtures** covering:
  - Clean typed English text
  - Clean typed French text (accented characters)
  - Mixed English/French documents
  - Dark background documents
  - Low-resolution scans
  - Receipt-style documents
  - Form layouts
  - Rotated pages
  - Number/date extraction
  - Multi-page PDFs

- **15 unit tests** covering:
  - Input validation
  - Image preprocessing
  - Image type detection
  - Engine availability checks
  - Pipeline execution with missing engine
  - Batch processing
  - v1.2 functionality preservation

---

## Technical Constraints

### Current Environment (Pixel 4a / Termux)

| Constraint | Value | Impact |
|------------|-------|--------|
| Architecture | ARM64 (aarch64) | Limits prebuilt wheel availability |
| Free Storage | ~3 GB | Heavy ML models (~2GB+) infeasible |
| Available RAM | ~832 MB | Neural OCR engines require 500MB-2GB |
| Python | 3.14.6 | Latest, some packages not yet compatible |
| NumPy | 2.4.4 | Available (foundation for image processing) |
| Pillow | 12.3.0 | Available (image I/O) |

### OCR Engine Status

| Engine | Availability | Status | Notes |
|--------|--------------|--------|-------|
| **Tesseract** | pkg install | ⚠️ Unavailable | Package repository connectivity issues; primary candidate when available |
| RapidOCR | pip wheel | ❌ No ARM64 wheel | Requires compilation on device (too slow/heavy) |
| EasyOCR | pip install | ❌ Rejected | Requires torch (~3.5GB), incompatible |
| PaddleOCR | pip install | ❌ Rejected | Requires paddlepaddle (~2GB), no ARM64 support |

---

## Installation (When Environment Allows)

```bash
# Install Tesseract OCR engine (primary candidate)
pkg install tesseract tesseract-data-eng tesseract-data-fra

# Verify installation
iconconvert ocr-status

# Test OCR functionality
iconconvert ocr tests/fixtures/ocr/clean_english.png
```

---

## Architecture

```
engine/
├── ocr_engine.py          # Engine abstraction + Tesseract/Dummy implementations
├── ocr_engine_research.md # Detailed engine research documentation
└── converters/
    ├── pdf_to_image.py    # PDF page rasterization
    └── ocr_pipeline.py    # Main OCR pipeline

tests/
├── test_ocr.py            # Unit tests for OCR components
└── fixtures/ocr/          # 10 test images covering various scenarios
```

---

## API Reference

### Running OCR

```python
from engine.converters.ocr_pipeline import run_ocr

result = run_ocr(
    input_path="document.png",      # or .pdf
    language="eng",                 # "fra", "deu", "spa", etc.
    profile="balanced",             # "fast", "balanced", "quality"
    mode="auto",                    # "auto" (smart) or "force"
    output_format="txt",            # "txt", "json", "html"
)

if result["success"]:
    print(result["text"])
    print(f"Confidence: {result['confidence']:.1%}")
else:
    print("Errors:", result["errors"])
```

### Checking Engine Status

```python
from engine.ocr_engine import get_ocr_manager

mgr = get_ocr_manager()
status = mgr.ocr_status()
# {'status': 'unavailable', 'primary_engine': 'none', ...}
```

### CLI Usage

```bash
# Check OCR status
iconconvert ocr-status

# Run OCR on image
iconconvert ocr document.png --language eng

# Run OCR on PDF with quality preprocessing
iconconvert ocr scan.pdf --profile quality --format json

# Run OCR on French document
iconconvert ocr document_francais.png --language fra
```

---

## Conversion Matrix

| Operation | Supported | Fidelity | Method |
|-----------|-----------|----------|--------|
| Image → Text (OCR) | ✅ Infrastructure ready | N/A | Engine-dependent |
| PDF → Images | ✅ | Native | pypdfium2 |
| Image Preprocessing | ✅ | Good | Pillow (grayscale, denoise, contrast) |
| Multi-language OCR | ⚠️ Pending | N/A | Tesseract (when available) |

---

## Roadmap

### v1.3.0 (Current)
- ✅ OCR pipeline infrastructure
- ✅ Preprocessing engine (Pillow-based)
- ✅ Engine abstraction layer
- ✅ Test fixtures and coverage
- ✅ CLI integration
- ⚠️ OCR recognition: **DELEGATED** to Tesseract (pending availability)

### v1.4.0 (Planned)
- 🔲 Tesseract integration (enable when package available)
- 🔲 Language pack management
- 🔲 Confidence threshold controls
- 🔲 Batch OCR processing improvements
- 🔲 OCR-specific performance benchmarks

---

## Limitations & Known Issues

1. **No OCR engine currently available** — Pipeline returns graceful error messages with installation instructions
2. **No OpenCV available** — Preprocessing limited to Pillow operations (no advanced filters)
3. **No Neural OCR** — Heavy engines (EasyOCR, PaddleOCR) incompatible with device constraints
4. **Termux repo issues** — Package repository connectivity preventing Tesseract installation

---

## Backward Compatibility

All v1.0/v1.1/v1.2 functionality preserved:
- ✅ 16 converter modules operational
- ✅ 55/55 existing tests passing
- ✅ HTTP API endpoints unchanged
- ✅ Android wrapper compatible
- ✅ CLI interface extended (not modified)

---

*Release Date: September 2026*
*Author: Divine Favour · ICON Studios*
*Device: Pixel 4a · Termux aarch64*
*Repository: https://github.com/penndivinefavour-lab/icon-docforge*
