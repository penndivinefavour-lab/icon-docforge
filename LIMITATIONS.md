# Known Limitations

ICON DocForge is a mature tool, but like any document conversion system, it has limitations. This document honestly discusses them, particularly around the challenging PDF→DOCX conversion path.

---

## PDF→DOCX: The Core Challenge

### The Problem

PDF (Portable Document Format) and DOCX (Word Document) are fundamentally different in their approach to document layout:

- **PDF** is a **fixed-layout** format. Every element has an absolute position on the page. The document "prints" to a canvas.
- **DOCX** is a **flow-layout** format. Elements are placed relative to each other, and the layout adjusts based on page size, margins, and font metrics.

This means PDF→DOCX conversion is **not a direct translation** — it's a **reconstruction**. The engine reads the PDF's content and tries to rebuild it as a Word document, but the result is always an approximation.

### What Works Well

✅ Single-column text documents
✅ Simple tables with basic formatting
✅ Documents with standard fonts (Arial, Times New Roman, etc.)
✅ Basic bold/italic/heading formatting
✅ Lists (bulleted and numbered)
✅ Page breaks and section breaks (basic)

### What Doesn't Work Well

❌ **Multi-column layouts** — Columns become sequential text blocks
❌ **Complex tables** — Nested tables, merged cells, and complex borders may not preserve
❌ **Embedded fonts** — Custom fonts in the PDF may not exist in the DOCX output
❌ **Precise positioning** — Absolute positioning in PDFs translates poorly to flow-layout
❌ **Vector graphics and diagrams** — Complex shapes become approximations
❌ **Header/footer positioning** — May appear at wrong locations
❌ **Text boxes** — Flow as normal paragraphs
❌ **Footnotes and endnotes** — Often lost or misplaced
❌ **Image wrapping** — Text wrapping around images rarely survives

### Quality Impact

| Document Type | Reconstruction Quality | Notes |
|--------------|:----------------------:|-------|
| Simple text report | ⭐⭐⭐⭐⭐ | Excellent — near-perfect |
| Standard business letter | ⭐⭐⭐⭐ | Very good |
| Multi-column newsletter | ⭐⭐ | Poor — columns become text |
| Complex table document | ⭐⭐ | Poor — table structure may break |
| Form with text boxes | ⭐ | Very poor — positions lost |
| Scanned/image PDF | ⭐ | Very poor — no OCR in v1.0.0 |

### Recommendations

- **Use PDF→DOCX for content extraction**, not for perfect layout preservation
- If you need a Word document, **create it in Word and export to PDF**, not the other way around
- For complex documents, consider **PDF→Images** as an alternative (preserves visual fidelity)
- Future versions may integrate **Tesseract OCR** for scanned PDFs

---

## Other Known Limitations

### Large Files
- Files over 50MB may cause memory issues on low-end devices
- Conversion timeout is 5 minutes by default; large files may exceed this

### Password-Protected Files
- Password-protected PDFs, DOCX, PPTX, and XLSX files are **not supported** in v1.0.0
- No decryption mechanism is implemented

### Image-Only PDFs
- PDFs that contain only images (scanned documents) cannot be converted to editable formats without OCR
- OCR support is planned for a future release

### Formula Preservation
- Excel formulas are converted to their computed values, not the formula itself
- Word equations may not survive DOCX↔PDF round-trips

### PPTX Animation and Transitions
- All animations, transitions, and timing are lost in PPTX→PDF conversion
- Each slide becomes a static image or page

### CSV Encoding
- CSV files with non-standard encodings may cause import issues
- UTF-8 is the recommended encoding

---

## Platform-Specific Limitations

### Android APK Limitations
- **Python runtime may not be available** on the device — see [ANDROID.md](ANDROID.md) for full details
- The conversion engine requires Python; if Python binaries aren't accessible, conversions will fail
- For full functionality, use Termux mode instead

### Termux Limitations
- Some ARM64 binaries may have compatibility issues on older Android versions
- Storage access requires explicit permission via `termux-setup-storage`

---

## Planned Fixes and Improvements

See [ROADMAP.md](ROADMAP.md) for the development roadmap and planned improvements.

---

## Reporting Issues

If you encounter conversion quality issues:

1. Note the source format and complexity
2. Describe what specifically went wrong
3. Include the input file if possible
4. File an issue on GitHub with the tag `conversion-quality`

Every report helps improve the conversion algorithms.
