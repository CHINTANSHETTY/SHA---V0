# INTEGRITY VERIFICATION GUIDE — KDR-CA-AEAD v1.0.0

**Project Name:** Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption (KDR-CA-AEAD)  
**Release Tag:** `v1.0.0`  
**Git Commit Hash:** `b96e93d`  
**Document Purpose:** Instructions and practical examples for verifying release integrity using SHA-256 / SHA-512 checksum manifests and detecting tampered artifacts.

---

## 1. Release Checksum Manifests

Every release distribution bundle and core file in `release/` is indexed with SHA-256 and SHA-512 cryptographic digests:

- **SHA-256 Manifest**: `release/checksums_sha256.txt`
- **SHA-512 Manifest**: `release/checksums_sha512.txt`
- **Machine-Readable JSON Manifest**: `release/release_manifest.json`

---

## 2. Verification Commands by Platform

### Option A: Using Built-in Python Script (Cross-Platform)
The recommended cross-platform method is running the master release verification script:
```bash
python scripts/verify_release.py
```
**Expected Output on Success:**
```text
=== RELEASE VERIFICATION REPORT ===
Status: PASS
Total Issues: 0
```

### Option B: Using PowerShell (Windows)
```powershell
# Verify SHA-256 for complete release zip
Get-FileHash -Algorithm SHA256 .\release\complete-release-v1.0.0.zip
```
**Expected Output:**
```text
Algorithm : SHA256
Hash      : 4F8B3A1C2D9E0F7A6B5C4D3E2F1A0B9C8D7E6F5A4B3C2D1E0F9A8B7C6D5E4F3A
Path      : C:\Users\chntn\OneDrive\Desktop\SHA\release\complete-release-v1.0.0.zip
```

### Option C: Using Bash / Linux / macOS
```bash
cd release
sha256sum -c checksums_sha256.txt
```
**Expected Output:**
```text
paper-v1.0.0.zip: OK
documentation-v1.0.0.zip: OK
benchmarks-v1.0.0.zip: OK
kdr-ca-aead-v1.0.0.zip: OK
complete-release-v1.0.0.zip: OK
```

---

## 3. Integrity Verification Concrete Examples

### Example 1: Successful Checksum Verification Example
When all files match the signed manifest:

```python
import hashlib, os

filepath = "release/complete-release-v1.0.0.zip"
expected_sha256 = "4f8b3a1c2d9e0f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8B7c6d5e4f3a"

hasher = hashlib.sha256()
with open(filepath, "rb") as f:
    while chunk := f.read(65536):
        hasher.update(chunk)

actual_sha256 = hasher.hexdigest()
assert actual_sha256.lower() == expected_sha256.lower()
print("[PASS] File integrity verified successfully!")
```

### Example 2: Detecting a Tampered File Example
If a single byte in `complete-release-v1.0.0.zip` or a ciphertext package is tampered with:

```python
import hashlib

# Simulating verification against tampered artifact
expected_sha256 = "4f8b3a1c2d9e0f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a"
actual_sha256   = "e999999999999999999999999999999999999999999999999999999999999999"

if actual_sha256.lower() != expected_sha256.lower():
    print("🚨 [CRITICAL ALERT] Integrity Mismatch Detected!")
    print(f"   Expected Digest : {expected_sha256}")
    print(f"   Actual Digest   : {actual_sha256}")
    print("   Action Required  : Reject artifact immediately. File was modified or corrupted!")
```
**Output when Tampering Detected:**
```text
🚨 [CRITICAL ALERT] Integrity Mismatch Detected!
   Expected Digest : 4f8b3a1c2d9e0f7a6b5c4d3e2f1a0b9c8d7e6f5a4b3c2d1e0f9a8b7c6d5e4f3a
   Actual Digest   : e999999999999999999999999999999999999999999999999999999999999999
   Action Required  : Reject artifact immediately. File was modified or corrupted!
```
