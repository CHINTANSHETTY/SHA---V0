# Maintainer Guide - KDR-CA-AEAD v1.0.0

## Routine Maintenance Tasks

1. **Dependency Monitoring**: Quarterly check of Python package requirements (`pytest`, `numpy`, `scipy`, `matplotlib`, `reportlab`).
2. **Regression Testing**: Run `pytest` before approving any pull request.
3. **Release Packaging**: Run `python scripts/build_distribution.py` to generate new release tags.
4. **Repository Certification**: Run `python scripts/final_repository_certification.py` after significant updates.
