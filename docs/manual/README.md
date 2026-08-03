# KDR-CA-AEAD User Manual & Operational Reference

This directory contains the official user manual, installation guide, configuration guide, operational procedures, troubleshooting, FAQs, quick reference, and automated manual build engine.

## Formats Available
- **User Manual HTML**: `docs/manual/user_manual.html`
- **User Manual PDF**: `docs/manual/user_manual.pdf`
- **User Manual Markdown**: `docs/manual/user_manual.md`
- **Validation Report**: `docs/manual/manual_validation_report.json`
- **Quick Reference**: `docs/manual/quick_reference.md`

## Regeneration Command
```powershell
$env:PYTHONPATH="."
python docs/manual/build_manual.py
```
