# Android APK Documentation

ICON DocForge is available as a native Android APK built with Capacitor. The app wraps the web interface in a native shell, keeping all conversion logic local.

## Overview

The Android APK uses [Capacitor](https://capacitorjs.com/) to wrap the DocForge web application in a native Android WebView. All conversion processing happens locally via the Python engine bundled in the APK.

**Key principle**: Your documents never leave your device. No internet required for core functionality.

---

## Download

**Latest release**: [Releases page](https://github.com/penndivinefavour-lab/icon-docforge/releases)

---

## Installation

### Method 1: Direct Download
1. Open the GitHub release page on your Android phone
2. Tap the `.apk` file to download
3. When download completes, tap the notification
4. If prompted about installing unknown apps, allow it for your browser/file manager
5. Tap **Install**

### Method 2: ADB
```bash
adb install app-debug.apk
```

### Method 3: Build from Source
```bash
cd android-apk
npm install
bash sync-assets.sh
npx cap add android
cd android
./gradlew assembleDebug
```

---

## Application Information

| Property | Value |
|----------|-------|
| App Name | ICON DocForge |
| Package ID | `com.iconstudios.docforge` |
| Version | 1.0.0 |
| Min Android | API 23 (Android 6.0 Marshmallow) |
| Target Android | API 34 (Android 14) |
| Orientation | Portrait (landscape supported) |
| Size | ~5-8 MB (debug) |

---

## Architecture

### WebView Configuration

The app uses Android's WebView with these settings enabled:

- **JavaScript** (required for all tools)
- **DOM Storage** (required for app state)
- **File Access** (required for file operations)
- **Database** (for local caching)
- **Hardware acceleration** (for smooth rendering)

### Capacitor Plugins

| Plugin | Purpose |
|--------|---------|
| `@capacitor/app` | App lifecycle events |
| `@capacitor/browser` | Open external links |
| `@capacitor/share` | Share converted files |
| `@capacitor/clipboard` | Copy text results |
| `@capacitor/keyboard` | Keyboard handling |
| `@capacitor/status-bar` | Status bar styling |

### Back Button Behavior

- Inside a tool → Goes back to previous screen
- On home screen → Exits the app

---

## Local HTTP Server

The APK starts a local HTTP server on port 8080 to bridge the web UI with the Python conversion engine. This runs automatically on app launch.

**Limitation**: In the Android APK context, the Python engine may have limited functionality compared to a full Termux installation. The server handles conversion requests from the WebView.

> See [Limitations](#limitations) below for details.

---

## Permissions

The app requests minimal permissions:

| Permission | Reason |
|------------|--------|
| `INTERNET` | Required by WebView (even for local content) |
| `ACCESS_NETWORK_STATE` | Used to detect connectivity |

**No permissions requested for:**
- Camera
- Location
- Contacts
- Storage (file operations use sandboxed app storage)
- Microphone
- Phone

---

## Limitations

### Python/Native Binaries in APK

The Android APK does **not** include a full Python runtime. Instead:

1. The Capacitor WebView loads the web UI
2. The local HTTP server attempts to start a Python process
3. **If Python is not available on the device**, the conversion engine will not function
4. On devices with Termux installed, Python may be accessible

**What this means in practice:**
- The web UI will load and display correctly
- Conversions that require the Python engine may fail if Python binaries are unavailable
- For full functionality, use Termux mode instead
- Future versions may bundle a lightweight Python runtime via [Chaquopy](https://chaquo.com/chaquopy/) or [BeeWare](https://beeware.org/)

### File Size
- The APK is larger than a pure web app due to the native shell (~5-8 MB)
- Additional Python libraries would increase size significantly

### Conversion Quality
- PDF→DOCX reconstruction quality is the same as in Termux mode
- Complex layouts may not perfectly preserve

---

## Building the APK

### Prerequisites
- Node.js 18+
- Java 17 (JDK)
- Android SDK (API 34)
- Gradle

### Build Steps
```bash
cd android-apk
npm install
bash sync-assets.sh
npx cap add android
cd android
./gradlew assembleDebug
```

### GitHub Actions Build (Recommended)
Push a tag to trigger automatic building:

```bash
git tag android-v1.0.0 && git push origin android-v1.0.0
```

The workflow will:
1. Set up Java, Android SDK, and Node.js
2. Install dependencies and sync assets
3. Build the debug APK
4. Upload as an artifact
5. Create a GitHub Release

### Signing
The default build produces an **unsigned debug APK**. For a signed release:

1. Generate a keystore (never commit to repo):
   ```bash
   keytool -genkey -v -keystore my-release-key.jks -keyalg RSA -keysize 2048 -validity 10000 -alias docforge
   ```
2. Add keystore credentials as GitHub Actions secrets
3. The release workflow will sign the APK automatically

**Never commit keystore files or passwords to the repository.**

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| App won't install | Enable "Unknown sources" in Settings → Security |
| App crashes on launch | Reinstall and ensure sync-assets.sh ran |
| Conversion fails | Python not available — use Termux mode instead |
| White screen | Clear app cache: Settings → Apps → DocForge → Clear cache |
| Slow performance | Close other apps; the device may be low on RAM |

---

## Privacy

- All conversion processing happens locally
- No data uploaded to any server
- No analytics, tracking, or telemetry
- No account system required

See [PRIVACY.md](PRIVACY.md) for full details.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0.0 | Sep 2026 | Initial Android release |
