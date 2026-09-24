# Conversion Matrix

Complete matrix showing every supported input→output combination, its conversion strategy, and quality status.

**Legend:**
- ✅ **Native**: Direct library support, high fidelity
- ⚙️ **Engine-assisted**: Uses the conversion engine with intermediate steps, good results
- 🔄 **Reconstructed**: Layout is rebuilt from extracted data, may differ from original
- ⚠️ **Approximate**: Result is an approximation of the original, quality loss expected
- ❌ **Unsupported**: Not currently possible

---

## PDF → All Formats

| To | Status | Method | Notes |
|----|:------:|--------|-------|
| PDF | ✅ Native | PyMuPDF | Re-save, optimize, or modify |
| DOCX | 🔄 Reconstructed | pdf2docx | Layout approximation. Multi-column, complex tables may not preserve. See [LIMITATIONS.md](LIMITATIONS.md) |
| PPTX | ⚙️ Engine-assisted | PDF→Images→PPTX | Each page becomes a slide with embedded image |
| XLSX | ❌ Unsupported | — | No reliable PDF table extraction in v1.0.0 |
| PNG/JPG/WebP | ✅ Native | PyMuPDF render | Page-by-page image render |
| CSV | ❌ Unsupported | — | No reliable text extraction to CSV structure |
| TXT | ⚙️ Engine-assisted | PyMuPDF text extract | Plain text extraction, loses formatting |

## DOCX → All Formats

| To | Status | Method | Notes |
|----|:------:|--------|-------|
| PDF | ✅ Native | python-docx + reportlab | Text, tables, and basic formatting preserved |
| DOCX | ✅ Native | python-docx | Edit and resave |
| PPTX | 🔄 Reconstructed | python-docx→PDF→PPTX | Text per slide, layout approximate |
| XLSX | ⚙️ Engine-assisted | Extract tables→openpyxl | Table content converted to spreadsheet |
| PNG/JPG/WebP | ✅ Native | python-docx→PDF→Images | Render document pages as images |
| CSV | ⚙️ Engine-assisted | Extract tables→CSV | Table data only, loses formatting |
| TXT | ✅ Native | python-docx text extract | Plain text content |

## PPTX → All Formats

| To | Status | Method | Notes |
|----|:------:|--------|-------|
| PDF | ✅ Native | python-pptx + pdf2docx/reportlab | Slides become PDF pages |
| DOCX | 🔄 Reconstructed | python-pptx→PDF→DOCX | Text content preserved, layout approximate |
| PPTX | ✅ Native | python-pptx | Edit and resave |
| XLSX | ❌ Unsupported | — | Slide content doesn't map cleanly to spreadsheet |
| PNG/JPG/WebP | ✅ Native | python-pptx→PDF→Images | Each slide as an image |
| CSV | ❌ Unsupported | — | — |
| TXT | ✅ Native | python-pptx text extract | Slide text content |

## XLSX → All Formats

| To | Status | Method | Notes |
|----|:------:|--------|-------|
| PDF | ✅ Native | openpyxl + reportlab | Each sheet becomes a PDF page |
| DOCX | ⚙️ Engine-assisted | Extract tables→python-docx | Table content in Word format |
| PPTX | ❌ Unsupported | — | Spreadsheet data doesn't map to slides |
| XLSX | ✅ Native | openpyxl | Edit and resave |
| PNG/JPG/WebP | ⚙️ Engine-assisted | Openpyxl→reportlab→Images | Render cells as images |
| CSV | ✅ Native | openpyxl | Direct export per sheet |
| TXT | ✅ Native | openpyxl text extract | Tab-separated values |

## CSV → All Formats

| To | Status | Method | Notes |
|----|:------:|--------|-------|
| PDF | ✅ Native | csv + reportlab | Table rendered as PDF |
| DOCX | ⚙️ Engine-assisted | csv→python-docx table | Table in Word format |
| PPTX | ❌ Unsupported | — | — |
| XLSX | ✅ Native | openpyxl | Direct import |
| PNG/JPG/WebP | ⚙️ Engine-assisted | csv→reportlab→Images | Table rendered as image |
| CSV | ✅ Native | csv module | Re-format or filter |
| TXT | ✅ Native | csv module | Tab-separated output |

## Image → All Formats

| To | Status | Method | Notes |
|----|:------:|--------|-------|
| PDF | ✅ Native | Pillow/PyMuPDF | Image becomes PDF page |
| DOCX | ✅ Native | Pillow→python-docx | Image embedded in Word |
| PPTX | ✅ Native | Pillow→python-pptx | Image on slide |
| XLSX | ❌ Unsupported | — | — |
| PNG/JPG/WebP | ✅ Native | Pillow | Format conversion, resize, compress |
| CSV | ❌ Unsupported | — | — |
| TXT | ❌ Unsupported | — | — |

---

## Quality Summary by Category

### High Fidelity (✅ Native)
- PDF↔Images (rendering)
- DOCX→PDF (text preservation)
- XLSX↔CSV (tabular data)
- Image format conversion
- PPTX→PDF (slide rendering)

### Moderate Fidelity (⚙️ Engine-assisted / 🔄 Reconstructed)
- PDF→DOCX (layout reconstruction — quality varies)
- DOCX↔PPTX (text preserved, layout approximate)
- XLSX→DOCX (table content preserved)
- CSV→DOCX/XLSX (data preserved)

### Not Supported (❌)
- PDF↔XLSX (no table extraction)
- PPTX↔XLSX
- CSV↔PPTX
- Image↔CSV/TXT

---

## Batch Conversion

Batch mode accepts a JSON configuration file:

```json
{
  "jobs": [
    {
      "input": "report.pdf",
      "output": "report.docx",
      "from": "pdf",
      "to": "docx"
    },
    {
      "input": "data.xlsx",
      "output": "data.pdf",
      "from": "xlsx",
      "to": "pdf"
    }
  ]
}
```

Each job is processed sequentially. The engine reports per-job status.
