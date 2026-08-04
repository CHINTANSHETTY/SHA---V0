# Contributing to KDR-CA-AEAD

Thank you for your interest in contributing to **KDR-CA-AEAD** (Keyed Dynamically-Reconfigured Cellular Automata with Authenticated Encryption)!

---

## Code of Conduct

We are committed to providing a welcoming, respectful, and collaborative environment for all contributors. Please maintain professional and respectful communication in issues, pull requests, and discussions.

---

## How to Contribute

### 1. Reporting Bugs & Issues
Before opening a new issue:
- Check existing open issues to avoid duplicates.
- Provide a clear, descriptive title.
- Include step-by-step reproduction instructions, Python version, OS details, and full error tracebacks.

> [!CAUTION]
> For security vulnerabilities, do **not** open a public issue. Email details directly to `shettyashwitha26@gmail.com` or `chntnshetty@gmail.com` per our [Security Guide](docs/security_guide.md).

### 2. Development & Pull Request Workflow

1. **Fork & Clone**:
   ```bash
   git clone https://github.com/CHINTANSHETTY/SHA---V0.git
   cd SHA---V0
   ```
2. **Create a Feature Branch**:
   ```bash
   git checkout -b feat/your-descriptive-branch-name
   ```
3. **Set Up Virtual Environment**:
   ```bash
   python -m venv venv
   # Activate virtualenv and install dependencies
   pip install -r requirements.txt
   ```
4. **Implement Changes & Add Tests**:
   - Write unit tests under `tests/unit/` or integration tests under `tests/integration/`.
   - Maintain PEP 8 formatting and include docstrings with type hints.
   - Maintain constant-time operations (`hmac.compare_digest`) for cryptographic procedures.
5. **Run Test Suite**:
   ```bash
   $env:PYTHONPATH="."
   python -m pytest
   ```
6. **Submit Pull Request**:
   - Push your branch to GitHub and open a Pull Request against `main`.
   - Reference any related issues in your PR description.

---

## Documentation Guidelines

- Keep all documentation in standard GitHub-Flavored Markdown.
- Update cross-references in [`docs/navigation.md`](docs/navigation.md) when adding new documentation pages.
