"""
KDR-CA-AEAD Cryptographic Package - Unified Public API Surface.

Phase 2.5 System Integration & Final Validation.
"""

from crypto.analysis.benchmark_runner import run_full_benchmark_suite
from crypto.analysis.final_validation import verify_end_to_end_pipeline
from crypto.analysis.security_analysis import run_full_security_analysis
from crypto.ca.engine import evolve, evolve_step
from crypto.engine.decrypt import decrypt_bytes, decrypt_payload
from crypto.engine.dynamic_ca import DynamicCAEngine
from crypto.engine.encrypt import encrypt_bytes, encrypt_payload
from crypto.engine.key_schedule import KeyMaterial, KeySchedule
from crypto.models.exceptions import (
    AuthenticationError,
    CryptoError,
    KeyDerivationError,
)
from crypto.models.package import EncryptedPackage
from crypto.primitives.hkdf import hkdf
from crypto.primitives.hmac import generate_hmac, verify_hmac

__all__ = [
    # High-level Authenticated Encryption & Decryption
    "encrypt_bytes",
    "encrypt_payload",
    "decrypt_bytes",
    "decrypt_payload",
    "EncryptedPackage",
    # Dynamic Key Schedule & CA Permutation Engine
    "KeySchedule",
    "KeyMaterial",
    "DynamicCAEngine",
    "evolve",
    "evolve_step",
    # Primitives & Models
    "hkdf",
    "generate_hmac",
    "verify_hmac",
    "CryptoError",
    "KeyDerivationError",
    "AuthenticationError",
    # Security Analysis & Benchmarking Framework
    "run_full_security_analysis",
    "run_full_benchmark_suite",
    "verify_end_to_end_pipeline",
]
