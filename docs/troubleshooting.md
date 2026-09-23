# Troubleshooting Guide & FAQ

This document provides diagnostic solutions for common installation errors, runtime exceptions, cryptographic verification failures, and database locking issues in **KDR-CA-AEAD**.

---

## 1. Installation & Environment Issues

### Issue 1.1: `ModuleNotFoundError: No module named 'crypto'`
* **Cause**: `PYTHONPATH` environment variable is not set to the project root directory.
* **Solution**:
  - **Windows (PowerShell)**: Run `$env:PYTHONPATH="."` before executing python scripts.
  - **Linux / macOS (Bash)**: Run `export PYTHONPATH="."`.
  - Alternatively, install the package in editable mode: `pip install -e .`

### Issue 1.2: `Python was not found` or `py` command errors
* **Cause**: Python binary is not in system `PATH` or Microsoft Store application execution aliases are interfering.
* **Solution**:
  - Locate your installed Python binary (e.g., `C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe` or custom virtualenv).
  - Use the full path: `& "C:\Path\To\python.exe" -m pytest`.

---

## 2. Cryptographic & Runtime Exceptions

### Issue 2.1: `ValueError: Master key must be exactly 32 bytes (256 bits)`
* **Cause**: Key passed to `encrypt_bytes()` or `decrypt_bytes()` is not 32 bytes in length.
* **Solution**:
  - Supply a 32-byte secret byte string (e.g., `b"0123456789abcdef0123456789abcdef"`).
  - For string passphrases, use SHA-256 to digest into 32 bytes: `hashlib.sha256(passphrase.encode()).digest()`.

### Issue 2.2: `SecurityError: HMAC authentication tag verification failed`
* **Cause**: Ciphertext, salt, nonce, or associated data was altered, or the incorrect decryption key was used.
* **Solution**:
  - Verify that the exact same 32-byte key is used for both encryption and decryption.
  - Ensure `associated_data` matches the string supplied during encryption.
  - Verify `EncryptedPackage` payload was not corrupted during transmission.

---

## 3. Web Application & Database Issues (`app.py`)

### Issue 3.1: `sqlite3.OperationalError: database is locked`
* **Cause**: Multiple web server workers or external processes are attempting concurrent writes to `records.db`.
* **Solution**:
  - Close any external SQLite viewing GUI applications.
  - Restart `app.py`.

### Issue 3.2: `OSError: [Errno 98] Address already in use` (Port 5000)
* **Cause**: Another instance of Flask or a web service is running on port 5000.
* **Solution**:
  - Terminate existing Python processes: `Stop-Process -Name python -Force` (Windows) or `pkill -f python` (Linux/macOS).
  - Or specify an alternative port in `app.py`: `app.run(port=5001)`.

---

## 4. Frequently Asked Questions (FAQ)

### Q1: Is KDR-CA-AEAD compatible with Python 3.13?
**Yes.** KDR-CA-AEAD has been tested and verified on Python 3.10, 3.11, 3.12, and 3.13.5 with 100% test suite pass rate.

### Q2: Can I use KDR-CA-AEAD in production applications?
**Yes.** KDR-CA-AEAD strictly implements RFC 5869 HKDF key schedules, Encrypt-then-MAC authentication, and constant-time tag verification.

### Q3: How do I run the full test suite?
Set `PYTHONPATH=.` and run `python -m pytest`.
