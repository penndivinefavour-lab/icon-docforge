# RELEASE CHECKLIST — ICON DocForge

## Pre-Release Checklist

### Code Quality
- [ ] All tests passing (minimum 73 tests)
- [ ] No linting errors
- [ ] No TODO/FIXME comments in production code
- [ ] Version numbers consistent across all files
- [ ] CHANGELOG.md updated

### Security Audit
- [ ] Localhost binding verified (127.0.0.1)
- [ ] No external network calls during conversion
- [ ] Path traversal prevention tested
- [ ] Subprocess safety verified (no shell injection)
- [ ] File size limits enforced
- [ ] Timeout controls in place
- [ ] Temp file cleanup verified

### Documentation
- [ ] README.md accurate and complete
- [ ] INSTALL_ANDROID.md updated
- [ ] SECURITY.md current
- [ ] PRIVACY.md reflects actual practices
- [ ] SUPPORT.md has current FAQ
- [ ] CHANGELOG.md has entry for this version
- [ ] CAPABILITY_MATRIX.md accurate

### APK Build
- [ ] Gradle build succeeds
- [ ] ProGuard configuration valid
- [ ] Keystore accessible (GitHub Secrets configured)
- [ ] APK size < 50MB
- [ ] Debug and release builds both work

### Testing
- [ ] Fresh install test passed
- [ ] Upgrade from previous version test passed
- [ ] First launch offline test passed
- [ ] File picker works (single file)
- [ ] File picker works (multiple files)
- [ ] DOCX → PDF conversion works
- [ ] Images → PDF conversion works
- [ ] PDF merge works
- [ ] PDF split works
- [ ] Result screen shows correctly
- [ ] Open result works
- [ ] Share result works
- [ ] Back button navigation works
- [ ] Settings page loads
- [ ] Diagnostics page works
- [ ] Error handling tested (corrupted files, large files, etc.)
- [ ] Airplane mode test passed
- [ ] Memory usage acceptable (< 200MB peak)
- [ ] Startup time < 3 seconds

### Privacy Compliance
- [ ] No analytics/tracking code present
- [ ] No crash reporting to third parties
- [ ] Privacy policy accessible in-app
- [ ] No personal data collected
- [ ] No device identifiers transmitted

### Release Assets
- [ ] APK signed with release key
- [ ] SHA-256 checksum generated
- [ ] Release notes written
- [ ] Screenshots taken (optional)
- [ ] Changelog entry added

### Post-Release
- [ ] GitHub Release created
- [ ] APK uploaded to release
- [ ] Checksum file uploaded
- [ ] README updated with download link
- [ ] Tag pushed to repository
- [ ] Branch merged to main (if applicable)

---

## Post-Release Monitoring

- [ ] Monitor GitHub Issues for bug reports
- [ ] Monitor GitHub Discussions for feature requests
- [ ] Respond to user questions within 48 hours
- [ ] Update documentation based on feedback

---

## Emergency Procedures

If a critical bug is discovered after release:

1. **Assess severity** - Is it a security issue? Data loss? Crash?
2. **Fix immediately** - Create hotfix branch from release tag
3. **Test thoroughly** - Run full test suite
4. **Release patch** - Create new patch version (e.g., v1.4.1)
5. **Notify users** - Update release notes and README
6. **Document** - Add to CHANGELOG under "Unreleased" section

---

*Last Updated: September 2026*
*Version: 1.4.0*
