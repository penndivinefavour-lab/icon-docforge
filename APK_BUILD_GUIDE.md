# ICON DocForge — Production APK Build Guide

## Architecture Overview

ICON DocForge uses a **WebView-based Android app** with a local HTTP API backend. The app bundles web assets (HTML/CSS/JS) and communicates with a Python engine via localhost.

## Required Dependencies

### Android
- Android SDK API 34
- Android Build Tools 34.0.0
- Java 17 (Temurin)
- Capacitor 6.x
- Cordova FileChooser / Android SAF

### Python (bundled in APK)
Must include in requirements.txt:
```
reportlab>=5.0.0
pypdfium2>=5.0.0
PyPDF2>=3.0.0
pdfplumber>=0.11.0
python-pptx>=1.0.0
openpyxl>=3.1.0
odfpy>=1.4.0
mammoth>=1.0.0
docx2txt>=0.8
xlsxwriter>=3.0.0
Pillow>=10.0.0
WeasyPrint>=60.0
```

### System Binaries (Termux-only, NOT bundled in APK)
- pandoc (for DOCX↔HTML, Markdown→PDF)
- poppler-utils (for PDF operations)
- tesseract (optional OCR, manual install)

## APK Build Process

### Step 1: Install Android SDK (GitHub Actions)
```yaml
- uses: actions/setup-java@v4
  with:
    distribution: 'temurin'
    java-version: '17'

- uses: android-actions/setup-android@v4
  with:
    api-level: 34
    build-tools: '34.0.0'
```

### Step 2: Setup Capacitor
```bash
cd android-apk
npm ci
npx cap add android
```

### Step 3: Sync Web Assets
```bash
mkdir -p android-apk/android/app/src/main/assets/www
cp -r ../../web/* android-apk/android/app/src/main/assets/www/
```

### Step 4: Build Debug APK
```bash
cd android-apk/android
./gradlew assembleDebug
```

### Step 5: Sign Release APK (Required for Distribution)
```bash
# Generate keystore (do this ONCE, save securely)
keytool -genkey -v -keystore docforge-release.keystore \
  -alias docforge \
  -keyalg RSA -keysize 2048 -validity 10000

# Sign APK
jarsigner -verbose -sigalg SHA256withRSA \
  -digestalg SHA256 \
  -keystore docforge-release.keystore \
  app-release.apk docforge

# Verify
apksigner verify --print-certs app-release.apk
```

### Step 6: Upload to GitHub Releases
```bash
gh release create v1.4.0 \
  --title "ICON DocForge v1.4.0" \
  --notes "Production-ready offline document converter" \
  app-release.apk \
  app-release.apk.sha256
```

## Security Considerations

### Localhost Binding
The HTTP API binds to `127.0.0.1` only. This is enforced in `engine/config.py`:
```python
API_HOST = os.environ.get("ICONDOCFORGE_HTTP_HOST", "127.0.0.1")
```

### Path Validation
All file paths are validated in `engine/utils.py`:
```python
def validate_path(filepath: str, base_dir: str = None) -> Path:
    resolved = Path(filepath).resolve()
    base = Path(base_dir).resolve()
    try:
        resolved.relative_to(base)
    except ValueError:
        raise ValueError(f"Path traversal detected: {filepath}")
    return resolved
```

### No Network Requests During Conversion
The app does not make any external network requests during conversion. The only network activity is:
- GitHub API calls (for updates, optional)
- Analytics (disabled by default)

### File Permission Handling
Use Android Storage Access Framework (SAF):
- Request `READ_EXTERNAL_STORAGE` for legacy devices
- Use `Intent.ACTION_OPEN_DOCUMENT` for Android 13+
- Copy selected files to app's private storage
- Process in temp directory
- Clean up after completion

## Testing Checklist

- [ ] App installs cleanly
- [ ] Home screen loads without errors
- [ ] File picker opens correctly
- [ ] DOCX → PDF conversion works
- [ ] Images → PDF conversion works
- [ ] PDF merge works
- [ ] PDF split works
- [ ] Result screen shows file info
- [ ] Share button works
- [ ] Open button works
- [ ] Settings/diagnostics page loads
- [ ] Privacy policy displays
- [ ] App works offline (airplane mode test)
- [ ] No crashes on error conditions
- [ ] Temp files cleaned up
- [ ] Back button navigation works

## Known Limitations

### APK-Specific
- Some converters require Python packages not available in minimal builds
- Large files (>50MB) may fail due to memory constraints
- OCR requires separate Tesseract installation

### Termux-Specific
- Full CLI access
- All engines available if dependencies installed
- Can install additional packages via pkg/pip

## Versioning

Semantic versioning: MAJOR.MINOR.PATCH

- MAJOR: Breaking changes (API, format support)
- MINOR: New features (new converters, UI improvements)
- PATCH: Bug fixes, security patches

Tag format: `v1.4.0`, `v1.4.1`, etc.
