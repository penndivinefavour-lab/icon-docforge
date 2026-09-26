# Installation Guide — ICON DocForge Android APK

## Download & Install

### From GitHub Releases

1. **Visit the Releases page**: https://github.com/penndivinefavour-lab/icon-docforge/releases
2. **Download the latest APK**: Look for `icon-docforge-v1.4.0.apk`
3. **Verify the checksum** (recommended):
   ```bash
   # On Termux or Linux
   sha256sum icon-docforge-v1.4.0.apk
   # Should match the SHA-256 listed on the release page
   ```

### Installing on Android

#### First-Time Install (Unknown Sources)

Android requires permission to install apps from sources other than the Play Store:

1. Download the APK
2. Tap to open — you'll see a security warning
3. Tap **Settings** in the warning dialog
4. Enable **Allow from this source**
5. Return and tap **Install**

#### Standard Install (Android 8+)

Most modern Android devices will show:
1. "This type of app can be harmful"
2. Tap **Install anyway**
3. Wait for installation to complete
4. Tap **Open** or **Done**

### Alternative: Install via Termux

If you have Termux installed:

```bash
# Download APK
wget https://github.com/penndivinefavour-lab/icon-docforge/releases/download/v1.4.0/icon-docforge-v1.4.0.apk

# Open the APK (requires Termux:API)
termux-open icon-docforge-v1.4.0.apk
```

## Verify Installation

After installing, verify:

1. **App Icon**: Should appear as a purple diamond with "D" on your home screen
2. **First Launch**: You should see the ICON DocForge home screen
3. **Permissions**: The app may request storage access — grant it for file operations
4. **Offline Mode**: Disconnect from network and verify the app still works

## Upgrading

To upgrade from a previous version:

1. Download the new APK
2. Install over the existing app (your data will be preserved)
3. The app will update automatically

## Uninstalling

To completely remove the app:

1. Long-press the app icon
2. Tap **App info** or **Uninstall**
3. Confirm uninstallation

**Note**: Uninstalling does NOT delete any converted files. Your output PDFs, images, and documents remain in their original locations.

## Troubleshooting

### "App not installed" Error

- Ensure you have sufficient storage space
- Try clearing your download folder and re-downloading
- Check that your Android version is 8.0 (API 26) or higher

### App Crashes on Launch

- Force stop the app: Settings → Apps → ICON DocForge → Force Stop
- Clear cache: Settings → Apps → ICON DocForge → Storage → Clear Cache
- Reinstall the APK

### Files Not Opening After Conversion

- Grant storage permissions: Settings → Apps → ICON DocForge → Permissions → Storage → Allow
- Some file managers may need explicit permission to view files created by other apps

### "Conversion Failed" Error

- Check file size (max 50MB)
- Ensure the input file is not corrupted
- Try a different file format if available
- Check available storage space

## Security Notes

- **No internet required**: Once installed, the app works entirely offline
- **No account needed**: No login, registration, or email required
- **No telemetry**: The app does not collect usage data or analytics
- **Local processing**: All conversions happen on your device

## Supported File Formats

| Format | Read | Write | Notes |
|--------|------|-------|-------|
| PDF | ✓ | ✓ | Full support |
| PNG/JPG/WebP | ✓ | ✓ | Image input only |
| DOCX | ✓ | ○ | Requires pandoc |
| XLSX/CSV | ✓ | ○ | Requires openpyxl |
| PPTX | ✓ | ○ | Requires python-pptx |
| Markdown | ✓ | ○ | Requires pandoc |

○ = Limited support (requires additional packages not bundled in APK)

## Getting Help

- **GitHub Issues**: https://github.com/penndivinefavour-lab/icon-docforge/issues
- **Email**: iconstudiosyde@gmail.com
- **Website**: Check README.md in the repository

---

*Last Updated: September 2026*
*Version: 1.4.0*
