# KDR-CA-AEAD API Documentation & Developer Reference

This directory contains the official API reference manual, developer guide, executable code examples, coverage report, and automated doc generator tooling.

## Documentation Formats Available
- **Coverage Report**: `docs/api/coverage_report.json`
- **HTML Site**: `docs/api/html/index.html`
- **PDF Reference**: `docs/api/pdf/kdr_ca_aead_developer_reference.pdf`
- **Markdown Suite**: `docs/api/markdown/*.md`
- **API Manifest**: `docs/api/api_manifest.md`

## Regeneration Command
```powershell
$env:PYTHONPATH="."
python docs/api/build_api_docs.py
```
