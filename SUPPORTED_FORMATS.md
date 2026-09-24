# Supported Formats

## Input Formats

| Format | Extension | MIME Type | Library | Notes |
|--------|-----------|-----------|---------|-------|
| PDF | `.pdf` | `application/pdf` | PyMuPDF, pdf2docx | Text and image-based PDFs supported |
| DOCX | `.docx` | `application/vnd.openxmlformats-officedocument.wordprocessingml.document` | python-docx | Word 2007+ format |
| PPTX | `.pptx` | `application/vnd.openxmlformats-officedocument.presentationml.presentation` | python-pptx | PowerPoint 2007+ format |
| XLSX | `.xlsx` | `application/vnd.openxmlformats-officedocument.spreadsheetml.sheet` | openpyxl | Excel 2007+ format |
| CSV | `.csv` | `text/csv` | Built-in | Comma-separated values |
| PNG | `.png` | `image/png` | Pillow | Lossless raster image |
| JPG/JPEG | `.jpg`, `.jpeg` | `image/jpeg` | Pillow | Lossy compressed image |
| WebP | `.webp` | `image/webp` | Pillow | Modern web image format |
| GIF | `.gif` | `image/gif` | Pillow | Animated GIF (first frame only) |
| BMP | `.bmp` | `image/bmp` | Pillow | Uncompressed raster image |
| TIFF | `.tiff` | `image/tiff` | Pillow | Tagged Image File Format |
| JSON | `.json` | `application/json` | Built-in | Structured data |
| TXT | `.txt` | `text/plain` | Built-in | Plain text |

## Output Formats

| Format | Extension | Library | Notes |
|--------|-----------|---------|-------|
| PDF | `.pdf` | PyMuPDF, reportlab | High-quality page rendering |
| DOCX | `.docx` | python-docx | Editable Word document |
| PPTX | `.pptx` | python-pptx | Editable PowerPoint |
| XLSX | `.xlsx` | openpyxl | Editable Excel spreadsheet |
| CSV | `.csv` | Built-in | Structured data export |
| PNG | `.png` | Pillow | Lossless image |
| JPG | `.jpg` | Pillow | Compressed image |
| WebP | `.webp` | Pillow | Modern web image |

---

## Format-Specific Notes

### PDF

- **Text-based PDFs**: High-quality extraction and conversion
- **Image-based PDFs**: Rendering to images works; text extraction is limited without OCR
- **Password-protected PDFs**: Not supported in v1.0.0
- **Multi-page PDFs**: Supported for rendering and conversion

### DOCX

- Full support for text, bold, italic, headings, lists, tables
- Complex formatting (nested tables, embedded objects) may not fully survive conversion
- Images embedded in DOCX are preserved during conversion to PDF

### PPTX

- Text, bullet points, and basic formatting preserved
- Slide transitions and animations are lost (not applicable to static formats)
- Embedded images are preserved

### XLSX

- Full support for cell data, formatting, formulas (formula values, not formulas)
- Charts and pivot tables are not preserved
- Multi-sheet support: exports to multiple CSV files or combined XLSX

### Images

- All supported input image formats can be converted to any other image format
- Resize, crop, and rotate operations available
- Quality settings adjustable for JPEG output

---

## Limitations by Format

See [LIMITATIONS.md](LIMITATIONS.md) for detailed discussion of conversion quality issues, especially PDF→DOCX reconstruction challenges.

---

## MIME Type Reference

```
application/pdf                    → .pdf
application/vnd.openxmlformats-officedocument.wordprocessingml.document  → .docx
application/vnd.openxmlformats-officedocument.presentationml.presentation  → .pptx
application/vnd.openxmlformats-officedocument.spreadsheetml.sheet  → .xlsx
text/csv                           → .csv
image/png                          → .png
image/jpeg                         → .jpg, .jpeg
image/webp                         → .webp
image/gif                          → .gif
image/bmp                          → .bmp
image/tiff                         → .tiff
application/json                   → .json
text/plain                         → .txt
```
