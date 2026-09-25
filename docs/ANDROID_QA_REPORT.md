# ICON DocForge v1.4.0 Android QA Report

Date: 2026-09-25
Branch: `v1.4-production-apk`

## Executive status

**NOT PRODUCTION READY.** The black-screen fix and frontend integration fix are implemented and the corrected debug APK builds successfully, but the Pixel 4a is not currently visible through ADB from the Termux session. Physical-device verification of the corrected APK is therefore still pending. No claim is made that the corrected APK has been installed or successfully exercised on the Pixel 4a.

## Blocking root causes fixed

### 1. Black screen

The production transformation had replaced the Capacitor activity with a bare `AppCompatActivity`. It created no WebView and no content view. The corrected `MainActivity` uses a plain Android WebView, loads `file:///android_asset/public/index.html`, enables JavaScript and DOM storage, handles back navigation/state, and exposes a private file output bridge.

### 2. Empty tool catalogue

The packaged shell rendered, but the frontend never initialized. The web entrypoint loaded `/js/app.js` as a root-relative URL. Under the Android `file://` origin this resolved outside the packaged `assets/public/` directory. The v1.4 loader also expected `window.DFTools[toolId]`, while the existing v1.2/v1.3/v1.4 tool modules register through `window.DFRegistry[id]`.

The fix uses document-relative runtime paths, restores the existing `DFRegistry` contract, maps diagnostics to `engine-diagnostic.js`, and packages the local engines with the WebView.

## Android frontend capabilities

The corrected source contains 12 catalogue entries and 14 tool-module files. The catalogue reports 9 Android-ready workflows and 3 unavailable workflows. The packaged APK contains the required local vendor libraries and the following real workflow modules:

- Images → PDF
- PDF merge
- PDF split
- PDF page reorder
- PDF page rotation
- PDF text extraction and phrase search
- CSV ↔ XLSX
- DOCX → PDF (reconstructed layout; explicit fidelity warning)
- Android capabilities/diagnostics

Unsupported Android cards are not advertised as functional:

- PDF → Images: page rasterization is not bundled
- PDF metadata editing: not bundled
- Markdown → PDF: not bundled

The prior Termux/Python engine remains in the repository for Termux use. It is not used as an Android dependency.

## Static and build verification

- CI run: `36117634828`
- CI result: PASS
- Frontend integration: PASS — 12 cards, 6 categories, `DFRegistry` loader
- JavaScript syntax checks: PASS
- Offline vendor assets: present
- APK size: 7,137,188 bytes
- APK SHA-256: `744bcce062c861f4563b62608c70c5a7967ac1f712e0f89adb8b9f16692cbe02`
- APK path: `apk-output/icon-docforge-v1.4.0-debug.apk`
- Package ID: `com.iconstudios.docforge.debug`
- Previous tags preserved: v1.0.0, v1.1.0, v1.2.0, v1.3.0, v1.4.0, v1.4.1

## Physical Pixel 4a QA

| Test | Result |
|---|---|
| ADB device discovery | BLOCKED — `adb devices` empty |
| Corrected APK install | NOT RUN |
| Corrected APK launch | NOT RUN |
| Tool catalogue visible on Pixel 4a | NOT VERIFIED |
| Search filtering on Pixel 4a | NOT VERIFIED |
| Images → PDF on Pixel 4a | NOT VERIFIED |
| PDF merge on Pixel 4a | NOT VERIFIED |
| PDF split on Pixel 4a | NOT VERIFIED |
| PDF text extraction/search on Pixel 4a | NOT VERIFIED |
| DOCX → PDF on Pixel 4a | NOT VERIFIED |
| Output open/share on Pixel 4a | NOT VERIFIED |
| Offline launch on Pixel 4a | NOT VERIFIED |

## Required next step

Make the Pixel 4a visible to the Termux ADB server, then install the corrected APK with `adb install -r apk-output/icon-docforge-v1.4.0-debug.apk`. Collect `adb logcat` during launch and run the workflows above before any production recommendation.

## Source changes

- `web/index.html`
- `web/js/app.js`
- `web/js/tools/runtime.js`
- `web/js/tools/image-to-pdf.js`
- `web/js/tools/pdf-merge.js`
- `web/js/tools/pdf-split.js`
- `web/js/tools/pdf-reorder.js`
- `web/js/tools/pdf-rotate.js`
- `web/js/tools/pdf-text-search.js`
- `web/js/tools/csv-xlsx.js`
- `web/js/tools/docx-to-pdf.js`
- `web/js/tools/engine-diagnostic.js`
- `web/js/vendor/*.js`
- `android-apk/android/app/src/main/java/com/iconstudios/docforge/MainActivity.kt`
- `.github/workflows/build-apk.yml`
- `tests/frontend_integration.js`
- `tests/test_android_frontend.py`
