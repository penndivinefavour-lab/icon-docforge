# Android APK — ICON DocForge v1.1

## Current State
The Android wrapper (`com.iconstudios.docforge`) exists as a Capacitor project structure at `android-apk/`. The project directory contains:
- `android-apk/android/` — Capacitor Android project structure (Java sources, Gradle, resources)
- `android-apk/www/` — Web asset directory (HTML, JS, CSS for PWA)

## How It Works
The Capacitor wrapper:
1. Loads `web/index.html` as the main UI via `android-webview`
2. Communicates with the local HTTP server (`localhost:8765`) via the Capacitor bridge
3. All conversion operations happen via the Python engine on the device

## Limitations
- Building a signed APK requires: Node.js, npm, Android SDK, Gradle, Java JDK
- The Capacitor project needs `package.json`, `capacitor.config.json`, and `sync-assets.sh` to be fully functional
- These files exist in the project structure but need the full Node.js toolchain to build
- Building an APK on Pixel 4a is impractical (limited RAM/storage)

## Recommended Build Path
```bash
# On a development machine (not the phone):
npm install -g @capacitor/cli
cd android-apk
npm install
npx cap copy android
npx cap open android
cd android && ./gradlew assembleRelease
```

## Alternative: GitHub Actions CI Build
The `.github/workflows/android.yml` workflow can build the APK remotely. See that workflow for details.

## Testing on Device
- Termux development: `python3 engine/cli.py doctor` confirms all engines working
- Web UI: Open `web/index.html` in any mobile browser
- HTTP API: `http://localhost:8765` on the device

## Package ID
- `com.iconstudios.docforge`

## Privacy
- APK runs all conversions locally via `localhost:8765`
- No network permissions required in AndroidManifest.xml
- All user data stays on device
