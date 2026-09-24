# Testing Documentation

## Overview

ICON DocForge includes an automated test suite covering unit tests, integration tests, and end-to-end conversion tests. All tests use real fixture files to validate actual conversion behavior.

---

## Test Structure

```
tests/
├── fixtures/
│   ├── docx/          # DOCX test documents
│   ├── pdf/           # PDF test documents
│   ├── pptx/          # PPTX test documents
│   ├── images/        # Image test files (PNG, JPG, WebP, etc.)
│   └── spreadsheet/   # XLSX and CSV test files
├── test_engine.py     # Core engine tests
├── test_conversions.py # Format-specific conversion tests
└── test_server.py     # HTTP server tests
```

---

## Fixture Files

| Category | Files | Purpose |
|----------|-------|---------|
| PDF | `sample_document.pdf`, `multi_page.pdf` | Test PDF text extraction, page rendering |
| DOCX | `sample_document.docx`, `long_document.docx`, `empty_document.docx` | Test DOCX→PDF, DOCX→DOCX, edge cases |
| PPTX | `sample_presentation.pptx` | Test PPTX→PDF conversion |
| Images | `red.png`, `green.jpg`, `blue_transparent.png`, `small.jpg`, `large_photo.png`, `test_image.webp`, `rotated.jpg` | Test image format conversion, resize, rotate |
| Spreadsheet | `sample_data.xlsx`, `sample_data.csv`, `sample_data.json` | Test XLSX↔CSV, data validation |

---

## Running Tests

### Run All Tests
```bash
python3 -m pytest tests/ -v
```

### Run Specific Test File
```bash
python3 -m pytest tests/test_engine.py -v
python3 -m pytest tests/test_conversions.py -v
```

### Run Specific Test
```bash
python3 -m pytest tests/test_conversions.py::test_pdf_to_docx -v
```

### Run with Coverage
```bash
python3 -m pytest tests/ --cov=engine --cov-report=html
```

### Run CI Tests (GitHub Actions)
```bash
# Tests run automatically on every push and PR
```

---

## Test Categories

### Unit Tests (`test_engine.py`)

Tests the core conversion engine:
- Format detection and validation
- File loading and error handling
- Converter registry
- Job queue management
- Timeout handling

### Conversion Tests (`test_conversions.py`)

Tests actual format conversions:
- PDF → DOCX (reconstruction quality check)
- DOCX → PDF (text preservation)
- PPTX → PDF (slide rendering)
- XLSX → CSV (data integrity)
- Image → PDF (rendering)
- Image format conversion (PNG→JPG→WebP)
- CSV → XLSX (data preservation)

### Server Tests (`test_server.py`)

Tests the HTTP API:
- `/health` endpoint responds correctly
- `/formats` returns supported format list
- `/convert` accepts and processes requests
- `/status/:id` returns correct job status
- `/download/:id` serves converted files
- Error handling for invalid requests

---

## Test Data Validation

Each test validates:

1. **File exists**: Output file is created
2. **File size**: Output is non-trivial (>0 bytes)
3. **Format validity**: Output file opens with the correct library
4. **Content integrity**: Key content is preserved in conversion
5. **Error handling**: Invalid inputs produce appropriate errors

### Example Test
```python
def test_pdf_to_docx():
    result = convert("tests/fixtures/pdf/sample_document.pdf", "/tmp/test_out.docx", "pdf", "docx")
    assert result["status"] == "success"
    assert os.path.exists("/tmp/test_out.docx")
    # Verify DOCX opens correctly
    doc = docx.Document("/tmp/test_out.docx")
    assert len(doc.paragraphs) > 0
```

---

## Continuous Integration

GitHub Actions runs the test suite automatically:

- **On every push**: Tests run on the latest code
- **On pull requests**: Tests must pass before merge
- **On tagged releases**: Full test suite + build

See [test.yml](.github/workflows/test.yml) for CI configuration.

---

## Manual Testing Checklist

For manual QA, verify:

- [ ] PDF → DOCX conversion produces a valid DOCX file
- [ ] DOCX → PDF conversion preserves text content
- [ ] Image format conversion (PNG→JPG→WebP) works
- [ ] XLSX → CSV preserves all data
- [ ] Server starts correctly on port 8080
- [ ] Web UI loads without errors
- [ ] File upload works with various sizes
- [ ] Error messages are clear for unsupported formats
- [ ] Batch conversion processes all jobs
- [ ] Temp files are cleaned up after conversion

---

## Known Test Limitations

1. **PDF→DOCX quality**: Tests verify that output is a valid DOCX, not that layout matches perfectly (see [LIMITATIONS.md](LIMITATIONS.md))
2. **Image comparison**: Pixel-perfect comparison is not done; structural checks are used instead
3. **Cross-platform**: Tests may behave differently on Android vs desktop due to filesystem differences
4. **Large files**: Test fixtures are small; performance with large files is not tested

---

## Adding New Tests

1. Add fixture file to `tests/fixtures/`
2. Create test function in appropriate test file
3. Use the `convert()` helper from `test_engine.py`
4. Validate output file exists and is valid format
5. Include edge case tests (empty files, corrupted files, unsupported formats)
