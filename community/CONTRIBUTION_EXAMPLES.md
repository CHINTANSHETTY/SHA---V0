# Contribution Examples & Templates

This document provides concrete templates and examples for contributing to **KDR-CA-AEAD**, including pull requests, bug reports, documentation updates, and feature requests.

---

## 1. Pull Request (PR) Template & Example

### Pull Request Title Format
`feat(crypto): add CFFI speedup for dynamic cellular automata rule execution`  
`fix(cli): resolve relative filepath parsing error in encrypt.py`  
`docs(publication): add IEEE submission guide checklist`

### Example PR Description

```markdown
## Description of Changes
Added Cython bindings for `ca_engine.py` to accelerate dynamic Wolfram rule state transitions.

## Type of Change
- [ ] Bug fix (non-breaking change fixing an issue)
- [x] New feature (non-breaking change adding functionality)
- [ ] Breaking change (fix or feature causing existing functionality to change)
- [ ] Documentation update

## Testing Performed
- [x] All 465+ unit tests passed (`pytest tests/`).
- [x] Throughput benchmark executed (`python crypto/benchmarking/benchmark_report.py`).
- [x] Verified zero memory leak on 10 MB payload encryption.

## Verification Checklist
- [x] My code follows the code style of this project.
- [x] I have updated documentation accordingly.
- [x] New unit tests added for new functionality.
```

---

## 2. Bug Report Template & Example

### Example Bug Report Issue

```markdown
**Describe the Bug**
Running `encrypt.py` with an empty string payload raises an unhandled `ValueError` instead of returning a valid empty ciphertext package.

**To Reproduce**
Steps to reproduce the behavior:
1. Run `python encrypt.py --input "" --key "32_Byte_Secret_Master_Key_12345678"`
2. See error: `ValueError: Payload length must be >= 1 byte`.

**Expected Behavior**
Should successfully encrypt empty payloads or return a clear user warning.

**Environment**
- OS: Windows 11
- Python Version: 3.10.4
- Repository Version: v1.0.0
```

---

## 3. Documentation Contribution Example

### Adding a New Guide
1. Create new Markdown document in `docs/`.
2. Add reference link to `docs/index.md` and `README.md`.
3. Submit PR titled `docs(user_guide): add memory tuning guide`.
