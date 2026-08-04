# Lessons Learned & Technical Insights

1. **Constant-Time Security**: Enforcing `hmac.compare_digest()` at the AEAD layer completely eliminates timing side-channel leaks during MAC tag verification.
2. **Cross-Platform Release Automation**: Normalizing file path separators (`/` vs `\`) in ZIP/TAR generation ensures cross-platform deep content verification across Windows, Linux, and macOS.
3. **FAIR Archival Standards**: Providing machine-readable manifests (`release_manifest.json`, `environment_snapshot.json`) significantly simplifies Zenodo and Software Heritage ingestion.
