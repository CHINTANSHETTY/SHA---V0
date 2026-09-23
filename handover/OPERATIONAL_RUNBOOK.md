# Operational Runbook - KDR-CA-AEAD v1.0.0

## Troubleshooting Procedures

### Procedure 1: Fixing Test Suite Environment Issues
If `pytest` reports `ModuleNotFoundError: No module named 'crypto'`:
```powershell
$env:PYTHONPATH="."
python -m pytest
```

### Procedure 2: Regenerating Release Archives & Checksums
```powershell
$env:PYTHONPATH="."
python scripts/build_distribution.py --ci
```

### Procedure 3: Re-Running Repository Certification Pass
```powershell
$env:PYTHONPATH="."
python scripts/final_repository_certification.py
```
