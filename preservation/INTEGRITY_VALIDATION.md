# Long-Term Integrity Validation Guide

Fixity verification procedures for validating long-term file integrity:
```powershell
$env:PYTHONPATH="."
python -c "import hashlib; print('ZIP SHA256:', hashlib.sha256(open('release/complete-release-v1.0.0.zip', 'rb').read()).hexdigest())"
```
Compare output against `release/checksums_sha256.txt`.
