# ICON DocForge

**Universal Document Converter — convert between PDF, DOCX, PPTX, XLSX, images, and more. Built for Termux, Android, and the web.**

ICON DocForge is a self-contained document conversion engine that runs entirely offline on your device. No cloud processing, no data uploads, no account required. All conversions happen locally using battle-tested open-source libraries.

![Version](https://img.shields.io/badge/version-1.2.0-blue)
![Platform](https://img.shields.io/badge/platform-Android%20%7C%20Termux%20%7C%20Web-green)
![License](https://img.shields.io/badge/license-MIT-gray)

---

## Features

- **Offline-first**: Every conversion runs locally on your device. Your documents never leave your phone or terminal.
- **Universal format support**: Convert between PDF, DOCX, PPTX, XLSX, CSV, images (PNG, JPG, WebP), and more.
- **Termux-native**: Full CLI access from any Android terminal.
- **Android APK**: Install as a native app with a polished web UI.
- **Privacy by design**: No telemetry, no analytics, no network calls during conversion.
- **Zero configuration**: Works out of the box in Termux or as an APK.

---

## Supported Conversions

| From → To | PDF | DOCX | PPTX | XLSX | Images | CSV |
|-----------|:---:|:----:|:----:|:----:|:------:|:---:|
| **PDF** | ✅ | ⚠️ Reconstructed | ⚠️ | ⚠️ | ✅ | ❌ |
| **DOCX** | ✅ | ✅ | ⚠️ | ⚠️ | ✅ | ✅ |
| **PPTX** | ✅ | ⚠️ | ✅ | ❌ | ✅ | ❌ |
| **XLSX** | ✅ | ⚠️ | ❌ | ✅ | ✅ | ✅ |
| **Images** | ✅ | ❌ | ❌ | ❌ | ✅ | ❌ |
| **CSV** | ❌ | ✅ | ❌ | ✅ | ❌ | ✅ |

> **Full details**: See [CONVERSION_MATRIX.md](CONVERSION_MATRIX.md)

---

## Quick Start

### Termux (Android Terminal)

```bash
# Install Termux from F-Droid (Play Store version is outdated)
# Then install dependencies:
pkg update && pkg upgrade
pkg install python python-pip pdf2docx python-docx python-pptx openpyxl Pillow

# Clone and run:
git clone https://github.com/penndivinefavour-lab/icon-docforge.git
cd icon-docforge
python3 engine.py --help
```

### Android APK

1. Download the latest release from the [Releases page](https://github.com/penndivinefavour-lab/icon-docforge/releases)
2. Install the APK (enable "Unknown sources" if prompted)
3. Open the app — the web UI loads immediately
4. All conversions work offline

### Web

Visit [icon-docforge.localhost](http://icon-docforge.localhost) or deploy to any static host.

---

## Architecture

ICON DocForge uses a **local HTTP server** pattern:

```
┌─────────────────────────────────────────┐
│  User Interface (Web UI)                 │
│  ├── Home screen with conversion table  │
│  ├── File upload / selection            │
│  └── Results display + download         │
└──────────────────┬──────────────────────┘
                   │ HTTP (localhost)
                   ▼
┌─────────────────────────────────────────┐
│  Python Conversion Engine                │
│  ├── pdf2docx (PDF→DOCX reconstruction) │
│  ├── python-docx (DOCX editing)         │
│  ├── python-pptx (PPTX manipulation)    │
│  ├── openpyxl (XLSX/CSV)               │
│  ├── PyMuPDF (PDF rendering)           │
│  └── Pillow (Image processing)          │
└─────────────────────────────────────────┘
```

The web UI communicates with the Python engine via a lightweight local HTTP server on `127.0.0.1:8080`. No data leaves the device.

> **Full details**: See [ARCHITECTURE.md](ARCHITECTURE.md)

---

## Privacy & Security

- **All processing is local** — documents are never uploaded to any server
- **No analytics or telemetry** of any kind
- **No authentication** required — no accounts, no login
- **No persistent storage** — converted files go to your chosen directory
- **Open source** — audit the code yourself

See [PRIVACY.md](PRIVACY.md) and [SECURITY.md](SECURITY.md) for full details.

---

## Limitations

- **PDF→DOCX is reconstruction, not perfect**: The original PDF layout is approximated. Complex multi-column layouts, embedded fonts, and precise positioning may not survive conversion. See [LIMITATIONS.md](LIMITATIONS.md).
- **Python dependency**: The Android APK bundles Python via Termux-compatible tooling. Some native binaries may have limited functionality compared to a full Termux installation.
- **Large files**: Files over 50MB may cause memory issues on low-end devices.
- **Image-only PDFs**: PDFs containing only images (scanned documents) require OCR which is not yet included in v1.0.0.

---

## Installation

### Prerequisites

- **Android** with Termux (for CLI mode)
- **Python 3.8+** and required pip packages (for Termux)
- **Node.js 18+** and Java 17 (for building the Android APK)

### Termux Setup

```bash
pkg update && pkg upgrade
pkg install python python-pip
pip install pdf2docx python-docx python-pptx openpyxl Pillow pymupdf flask
```

See [TERMUX_SETUP.md](TERMUX_SETUP.md) for a detailed walkthrough.

### Android APK Build

```bash
cd android-apk
npm install
bash sync-assets.sh
npx cap add android
cd android
./gradlew assembleDebug
```

See [ANDROID.md](ANDROID.md) for full details.

---

## CLI Reference

```bash
python3 engine.py --input file.pdf --output output.docx --from pdf --to docx
python3 engine.py --batch conversions.json
python3 engine.py --server --port 8080
python3 engine.py --help
```

See [CLI.md](CLI.md) for complete reference.

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError` | Run `pip install -r requirements.txt` |
| APK crashes on launch | Ensure `sync-assets.sh` was run before building |
| Conversion fails | Check file format support in [CONVERSION_MATRIX.md](CONVERSION_MATRIX.md) |
| Port 8080 already in use | Use `--port 8081` or kill the conflicting process |
| PDF→DOCX output looks wrong | This is expected for complex layouts — see [LIMITATIONS.md](LIMITATIONS.md) |

---

## Contributing

Contributions welcome! Please read [ROADMAP.md](ROADMAP.md) for planned features and [TESTING.md](TESTING.md) for test procedures.

---

## License

MIT License — see [LICENSE](LICENSE) for details.
