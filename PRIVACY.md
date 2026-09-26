# PRIVACY POLICY — ICON DocForge

**Effective Date:** September 2026  
**Version:** 1.4.0  
**Developer:** ICON Studios  
**Contact:** iconstudiosyde@gmail.com

## Introduction

ICON DocForge is an offline document conversion application designed with privacy as a core principle. This policy explains how we handle your data—and more importantly, how we **do not** handle your data.

## Data We Collect

### We Do NOT Collect

**Zero data is collected by ICON DocForge:**

- ✗ No document contents
- ✗ No document metadata
- ✗ No file paths or names
- ✗ No conversion history stored remotely
- ✗ No device identifiers
- ✗ No IP addresses
- ✗ No usage statistics
- ✗ No crash reports sent to third parties
- ✗ No analytics data

## How the App Works

### Local Processing Only

All document conversions happen **entirely on your device**:

1. You select a file from your device storage
2. The file is copied to the app's private temporary directory
3. The app's built-in Python engine processes the file
4. The converted output is generated in the same temporary directory
5. You choose to open, share, or save the result
6. Temporary files are deleted

**At no point are your documents transmitted anywhere.**

### Network Activity

The app makes **zero network requests** during normal operation. The only network-related functionality is:

- Optional: Checking for app updates (disabled by default)
- Required: Capacitor WebView bridge (internal communication only)

Both occur exclusively between the app and itself—no external servers are contacted.

## Data Stored on Your Device

### Temporary Files

- **Location:** App's private temp directory
- **Lifetime:** Deleted immediately after conversion (success or failure)
- **Content:** Same as your input files + converted output
- **Access:** Only the app can access these files

### Local Storage

- **Location:** Android SharedPreferences
- **Content:** App preferences, conversion history (local only)
- **Duration:** Persist until app uninstall
- **Purpose:** Remember your settings and recent conversions

### No Cloud Storage

We do not use:
- Cloud databases
- Remote file storage
- Backup services
- Sync services

## Third-Party Services

### None Used

ICON DocForge does not integrate with any third-party services, including:

- ✗ Google Analytics
- ✗ Firebase
- ✗ Crashlytics
- ✗ AdMob
- ✗ Social media APIs
- ✗ Payment processors
- ✗ Email services

### Open Source Libraries

The app uses open-source libraries, but they operate locally:

| Library | Purpose | Data Exposure |
|---------|---------|---------------|
| ReportLab | PDF generation | None |
| python-docx | DOCX handling | None |
| Pillow | Image processing | None |
| pypdfium2 | PDF rendering | None |
| Pandoc | Format conversion | None |

These libraries process data locally and do not transmit anything externally.

## Children's Privacy

ICON DocForge is not intended for children under 13. However, since we collect no data whatsoever, this policy applies equally to all users regardless of age.

## Data Retention

Since we collect no data, there is nothing to retain. Temporary files are deleted immediately after use.

## Your Rights

Under GDPR and other privacy laws, you have the right to:

- **Access:** There is no data to access
- **Rectification:** There is no data to correct
- **Erasure:** There is no data to erase
- **Portability:** There is no data to export
- **Objection:** You may object to processing at any time (there is no processing)

## Changes to This Policy

We may update this privacy policy occasionally. Changes will be:

1. Posted in the app's Settings screen
2. Updated in the repository README
3. Reflective of actual data practices

Since we collect no data, changes are unlikely but possible if we add new features.

## Contact Us

If you have questions about this privacy policy:

- **Email:** iconstudiosyde@gmail.com
- **GitHub:** https://github.com/penndivinefavour-lab/icon-docforge/issues
- **In-App:** Settings → About → Contact Developer

## Conclusion

**Your documents are your documents.** They never leave your device. We cannot see them, share them, sell them, or analyze them. This is not a feature—it is the fundamental design principle of ICON DocForge.

Thank you for trusting us with your documents.

---

*ICON Studios · Yaoundé, Cameroon*  
*Made with care for privacy-conscious users*
