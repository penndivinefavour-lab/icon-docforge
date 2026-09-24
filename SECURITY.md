# Security Considerations

## Overview

ICON DocForge is designed with security as a core principle. All conversions happen locally with no network transmission. This document outlines the security architecture, potential risks, and mitigation strategies.

---

## Security Architecture

### Local-Only Processing

- The conversion engine binds to `127.0.0.1` (localhost only)
- **No external network access** during conversion
- No outbound connections of any kind
- The HTTP server is not exposed to other devices by default

### File Validation

All input files are validated before processing:

1. **Magic byte verification**: Confirms the file matches the claimed format
2. **Size limits**: Files over 50MB are rejected (configurable)
3. **Extension validation**: File extension must match actual content type
4. **Sandbox isolation**: All files are copied to `/tmp/docforge/{uuid}/` with restricted permissions

### Input Sanitization

- File paths are normalized to prevent directory traversal attacks
- Filenames are sanitized (no special characters, no path separators)
- Temporary files use UUID-based names to prevent guessing

---

## Threat Model

### What We Protect Against

| Threat | Mitigation |
|--------|-----------|
| Malicious file upload | Magic byte validation, size limits, sandbox isolation |
| Directory traversal | Path normalization, filename sanitization |
| Local network exposure | Binds to localhost only by default |
| Data leakage | No persistent storage, temp files cleaned up |
| Denial of service | Conversion timeout (default 5 min), file size limits |
| Privilege escalation | Runs with least-privilege user permissions |

### What We Don't Protect Against

- **Physical device access**: If someone has physical access to your device, they can access files
- **Rooted devices**: Security model assumes a non-rooted device
- **Malware on device**: If the device is compromised, all bets are off

---

## Data Handling

### In Transit
- N/A — no data is transmitted over networks during conversion

### At Rest
- Temporary files are stored in `/tmp/docforge/` with `0600` permissions
- Files are deleted immediately after conversion completes
- No conversion history is persisted

### In Memory
- Files are loaded into memory for processing
- Memory is zeroed after use where possible (Python's GC handles this)

---

## Dependencies

All Python dependencies are open-source and well-maintained:

| Library | License | Security Status |
|---------|---------|-----------------|
| pdf2docx | MIT | No known vulnerabilities |
| python-docx | MIT | No known vulnerabilities |
| python-pptx | MIT | No known vulnerabilities |
| openpyxl | MIT | No known vulnerabilities |
| Pillow | HPND | No known vulnerabilities |
| PyMuPDF | GNU AFFERO GPL 3 | No known vulnerabilities |
| Flask | BSD-3-Clause | No known vulnerabilities |

### Dependency Security
- Run `pip audit` to check for known vulnerabilities
- Update packages regularly: `pip install --upgrade`
- Pin versions in `requirements.txt` for reproducible builds

---

## Android-Specific Considerations

### WebView Security
- JavaScript enabled (required for functionality)
- Content loaded from `file://` scheme (local assets only)
- No mixed content (HTTP loaded from HTTPS page)
- WebView debugging disabled in release builds

### APK Security
- Default build is unsigned debug APK
- Release builds must be signed with a keystore
- Keystore passwords must never be committed to source control
- ProGuard is enabled in release builds for code obfuscation

---

## Known Vulnerabilities

### PDF Parsing
- PDF files can contain malicious content (JavaScript, embedded exploits)
- **Mitigation**: PyMuPDF uses a hardened parser; avoid opening untrusted PDFs
- **Recommendation**: Process PDFs in a sandboxed environment if handling untrusted sources

### Temp File Race Conditions
- Theoretical race condition between file creation and validation
- **Mitigation**: UUID-based filenames, filesystem-level isolation

---

## Best Practices for Users

1. **Only convert files you trust** — even local processing can have edge cases
2. **Keep the app updated** — security patches are delivered via updates
3. **Review permissions** — the app requests minimal permissions
4. **Delete temp files** — manually clean `/tmp/docforge/` if needed
5. **Use HTTPS for web access** — if exposing the server over a network

---

## Security Auditing

To audit the codebase:

```bash
# Check for dependency vulnerabilities:
pip audit

# Scan for common security issues:
bandit -r engine.py

# Review network bindings:
grep -r "0.0.0.0" engine.py
grep -r "socket" engine.py
```

---

## Responsible Disclosure

If you discover a security vulnerability, please report it privately to the maintainers at [iconstudios@protonmail.com](mailto:iconstudios@protonmail.com). Do not disclose publicly until a fix is available.
