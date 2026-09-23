"""
Module:
    __init__.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Documentation Review & API Validation Subsystem (Phase 4.4).

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)
"""

from crypto.documentation.api_validator import (
    validate_module_docstrings,
    validate_code_examples,
    run_api_validation_suite,
)
from crypto.documentation.documentation_review import (
    review_project_documentation,
    generate_documentation_reports,
)

__all__ = [
    "validate_module_docstrings",
    "validate_code_examples",
    "run_api_validation_suite",
    "review_project_documentation",
    "generate_documentation_reports",
]
