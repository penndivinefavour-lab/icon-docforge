# Engine Research — ICON DocForge v1.1

## Investigated Engines and Tools

### 1. GhostScript (❌ NOT AVAILABLE)
- **Package**: `ghostscript` in Termux
- **Status**: Not available in Termux repository
- **Purpose**: PDF compression, watermarking, advanced PDF operations
- **Finding**: Cannot be installed via `pkg install ghostscript`. Bionic libc incompatibility for some builds.
- **Alternative**: Used Poppler tools (pdftoppm, pdfunite, pdfseparate) + PyPDF2 for equivalent functionality
- **Decision**: Skipped Ghostscript; implemented compression via pdftoppm re-rendering and watermark via PyPDF2 metadata

### 2. ImageMagick (❌ NOT AVAILABLE)
- **Package**: `imagemagick` in Termux
- **Status**: Not available on this device
- **Purpose**: Image conversion, PDF creation from images
- **Finding**: Not installable via Termux packages on aarch64
- **Alternative**: Used Pillow (Python) for image processing + fpdf2 for image→PDF
- **Decision**: Pillow provides sufficient image manipulation; fpdf2 handles image→PDF well

### 3. LibreOffice (❌ NOT AVAILABLE)
- **Package**: `libreoffice` in Termux
- **Status**: Not available; too heavy for Android
- **Purpose**: Office document conversion (PPTX→PDF, DOCX→PDF with formatting)
- **Finding**: Not in Termux repositories; requires ~500MB+ storage and significant RAM
- **Alternative**: Pandoc for DOCX→PDF (via HTML→weasyprint), python-pptx for PPTX manipulation
- **Decision**: Accept limitation; PPTX→PDF not available locally

### 4. QPDF (❌ NOT AVAILABLE)
- **Package**: `qpdf` in Termux
- **Status**: Not available
- **Purpose**: PDF manipulation (merge, split, encrypt, decrypt)
- **Finding**: Not in Termux repository
- **Alternative**: pdfunite (Poppler) for merge, pdfseparate for split, PyPDF2 for metadata/encryption
- **Decision**: Poppler tools provide equivalent core functionality

### 5. pdf2docx (✅ INVESTIGATED, NOT INSTALLED)
- **Package**: `pdf2docx` from PyPI
- **Size**: ~2.3 MB wheel + PyMuPDF dependency (~88 MB source)
- **Purpose**: PDF → editable DOCX reconstruction
- **Finding**: Would require PyMuPDF (fitz) which needs compilation or large prebuilt wheel
- **Status**: Download started but timed out on Pixel 4a (limited RAM/storage)
- **Decision**: Deferred to Phase 2; PDF→DOCX is fundamentally difficult (layout vs semantics)
- **Honest Assessment**: Even if installed, reconstruction quality is approximate — PDFs describe page layout, not document structure

### 6. pdftotext (✅ AVAILABLE)
- **Package**: `poppler-utils` (includes pdftotext)
- **Status**: ✅ Working
- **Purpose**: PDF text extraction, search
- **Finding**: `pdftotext file.pdf -` extracts all text; supports page ranges
- **Decision**: Primary tool for PDF→text extraction and text search

### 7. Poppler Tools (✅ AVAILABLE)
- **Tools**: pdftoppm, pdftotext, pdfunite, pdfseparate, pdfinfo
- **Version**: 26.02.0
- **Status**: ✅ All working
- **Decision**: Core PDF engine for all PDF operations

### 8. PyMuPDF/fitz (✅ INVESTIGATED)
- **Package**: `PyMuPDF` from PyPI
- **Size**: ~15 MB wheel
- **Purpose**: Advanced PDF manipulation (text extraction, page rendering, annotations)
- **Finding**: Better API than PyPDF2; could replace some Poppler functions
- **Decision**: Not installed; current PyPDF2 + Poppler combination sufficient

### 9. pdf2image (✅ AVAILABLE)
- **Package**: `pdf2image` (Python)
- **Version**: 1.17.0
- **Status**: ✅ Working (requires pdftoppm backend)
- **Purpose**: Convert PDF pages to PIL images
- **Decision**: Working but uses pdftoppm internally; direct pdftoppm calls preferred

### 10. Tesseract OCR (❌ NOT AVAILABLE)
- **Package**: `tesseract-ocr` in Termux
- **Status**: Not available
- **Purpose**: OCR for scanned/image-only PDFs
- **Finding**: Not in Termux repository
- **Decision**: OCR deferred; only relevant for scanned documents, not digital PDFs

### 11. pdf2docx (Alternative: pdftotext + layout analysis)
- **Status**: Investigated but not implemented
- **Finding**: PDF→DOCX is fundamentally limited because PDFs store layout (x,y coordinates) not document structure (headings, paragraphs, tables)
- **Honest Assessment**: Any PDF→DOCX conversion will be approximate reconstruction, not faithful reproduction of original document semantics
- **Decision**: Document as "Reconstructed/Approximate" in conversion matrix

## Summary Table

| Engine | Available | Used | Decision |
|--------|-----------|------|----------|
| GhostScript | ❌ | ❌ | Skipped; use Poppler |
| ImageMagick | ❌ | ❌ | Skipped; use Pillow |
| LibreOffice | ❌ | ❌ | Skipped; too heavy |
| QPDF | ❌ | ❌ | Skipped; use pdfunite/pdfseparate |
| pdf2docx | ⚠️ | ❌ | Deferred; fundamentally limited |
| pdftotext | ✅ | ✅ | Primary PDF text extraction |
| Poppler | ✅ | ✅ | Core PDF engine |
| PyMuPDF | ✅ | ❌ | Not needed for current features |
| pdf2image | ✅ | ✅ | PDF→image (uses pdftoppm) |
| Tesseract | ❌ | ❌ | Not available; not needed for digital PDFs |
| Pandoc | ✅ | ✅ | DOCX/ODT/Markdown conversions |
| WeasyPrint | ✅ | ✅ | HTML→PDF |
| FPDF2 | ✅ | ✅ | Image→PDF |
| ReportLab | ✅ | ✅ | PDF generation |
| python-docx | ✅ | ✅ | DOCX manipulation |
| python-pptx | ✅ | ✅ | PPTX manipulation |
| openpyxl | ✅ | ✅ | XLSX manipulation |
| Pillow | ✅ | ✅ | Image processing |
| PyPDF2 | ✅ | ✅ | PDF metadata, watermark, reorder |

## Licensing Notes

All engines used are open-source and redistributeable:
- Poppler: LGPL
- Pandoc: GPL v2+
- ReportLab: BSD
- WeasyPrint: BSD
- FPDF2: MIT
- python-docx: MIT
- python-pptx: MIT
- openpyxl: MIT
- Pillow: HPND/MIT
- PyPDF2: BSD
- pdf2image: MIT

All licenses are compatible with redistribution in GitHub repository and Android APK.
