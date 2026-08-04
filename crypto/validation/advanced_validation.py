"""
Module:
    advanced_validation.py

Project:
    KDR-CA-AEAD Cryptographic Research Engine

Purpose:
    Advanced Input Validation & Boundary Enforcement Subsystem (Phase 4.1).
    Provides comprehensive input validation routines for master keys, salts, nonces, payloads,
    encrypted packages, CA rule tables, HMAC tags, and HKDF expansion parameters to ensure
    robust error handling and reject malformed inputs before cryptographic processing.

Author:
    Nagamrutha (Security Analysis & Cryptographic Validation Lead)

IEEE Mapping:
    Section IX-A – Advanced Input Validation & Fault Tolerance Architecture
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Sequence, TypeAlias

from crypto.constants import DEFAULT_NONCE_LENGTH, DEFAULT_SALT_LENGTH, HMAC_TAG_LENGTH, HKDF_MAX_OUTPUT
from crypto.models.exceptions import CorruptedPayloadError, CryptoError, KeyDerivationError
from crypto.models.package import EncryptedPackage

__all__ = [
    "validate_master_key",
    "validate_salt",
    "validate_nonce",
    "validate_payload_data",
    "validate_encrypted_package",
    "validate_ca_rule_table",
    "validate_hmac_tag",
    "validate_hkdf_parameters",
    "run_comprehensive_system_validation",
    "BytesLike",
]

BytesLike: TypeAlias = bytes | bytearray


def validate_master_key(master_key: Any) -> bytes:
    """Validates master key or password buffer.

    Preconditions:
      - master_key must not be None or empty.
      - master_key must be bytes, bytearray, or non-empty str.

    Returns:
        Validated master key as bytes.

    Raises:
        CryptoError: If master key type is invalid or empty.
    """
    if master_key is None:
        raise CryptoError("Master key cannot be None.")

    if isinstance(master_key, str):
        if not master_key.strip():
            raise CryptoError("Master key string cannot be empty or whitespace-only.")
        key_bytes = master_key.encode("utf-8")
    elif isinstance(master_key, (bytes, bytearray)):
        key_bytes = bytes(master_key)
    else:
        raise CryptoError(f"Invalid master key type '{type(master_key).__name__}'. Expected bytes, bytearray, or str.")

    if len(key_bytes) == 0:
        raise CryptoError("Master key buffer cannot be 0 bytes.")

    return key_bytes


def validate_salt(salt: Any, expected_length: int = DEFAULT_SALT_LENGTH) -> bytes:
    """Validates salt buffer type and length.

    Returns:
        Validated salt as bytes.

    Raises:
        CryptoError: If salt is None, not bytes-like, or has invalid length.
    """
    if salt is None:
        raise CryptoError("Salt cannot be None.")

    if not isinstance(salt, (bytes, bytearray)):
        raise CryptoError(f"Invalid salt type '{type(salt).__name__}'. Expected bytes or bytearray.")

    salt_bytes = bytes(salt)
    if len(salt_bytes) != expected_length:
        raise CryptoError(f"Invalid salt length {len(salt_bytes)} bytes. Expected exactly {expected_length} bytes.")

    return salt_bytes


def validate_nonce(nonce: Any, expected_length: int = DEFAULT_NONCE_LENGTH) -> bytes:
    """Validates nonce buffer type and length.

    Returns:
        Validated nonce as bytes.

    Raises:
        CryptoError: If nonce is None, not bytes-like, or has invalid length.
    """
    if nonce is None:
        raise CryptoError("Nonce cannot be None.")

    if not isinstance(nonce, (bytes, bytearray)):
        raise CryptoError(f"Invalid nonce type '{type(nonce).__name__}'. Expected bytes or bytearray.")

    nonce_bytes = bytes(nonce)
    if len(nonce_bytes) != expected_length:
        raise CryptoError(f"Invalid nonce length {len(nonce_bytes)} bytes. Expected exactly {expected_length} bytes.")

    return nonce_bytes


def validate_payload_data(data: Any, max_bytes: int = 100 * 1024 * 1024) -> bytes:
    """Validates payload data buffer for encryption/decryption.

    Returns:
        Validated payload data as bytes.

    Raises:
        CryptoError: If payload is None, empty, or exceeds maximum length bound.
    """
    if data is None:
        raise CryptoError("Payload data cannot be None.")

    if isinstance(data, str):
        if len(data) == 0:
            raise CryptoError("Payload text cannot be empty.")
        data_bytes = data.encode("utf-8")
    elif isinstance(data, (bytes, bytearray)):
        data_bytes = bytes(data)
    else:
        raise CryptoError(f"Invalid payload type '{type(data).__name__}'. Expected bytes, bytearray, or str.")

    if len(data_bytes) == 0:
        raise CryptoError("Payload data buffer cannot be empty (0 bytes).")

    if len(data_bytes) > max_bytes:
        raise CryptoError(f"Payload size ({len(data_bytes)} bytes) exceeds maximum limit ({max_bytes} bytes).")

    return data_bytes


def validate_encrypted_package(package: Any) -> EncryptedPackage:
    """Validates EncryptedPackage dataclass integrity and component bounds.

    Returns:
        Validated EncryptedPackage instance.

    Raises:
        CorruptedPayloadError / CryptoError: If package schema, field types, or lengths are invalid.
    """
    if package is None:
        raise CorruptedPayloadError("EncryptedPackage instance cannot be None.")

    if not isinstance(package, EncryptedPackage):
        raise CorruptedPayloadError(f"Invalid package object type '{type(package).__name__}'. Expected EncryptedPackage.")

    if not package.version or not isinstance(package.version, str):
        raise CorruptedPayloadError("Package protocol version must be a non-empty string.")

    validate_salt(package.salt)
    validate_nonce(package.nonce)

    if not isinstance(package.ciphertext, (bytes, bytearray)):
        raise CorruptedPayloadError("Package ciphertext must be a bytes-like buffer.")

    if len(package.ciphertext) == 0:
        raise CorruptedPayloadError("Package ciphertext cannot be empty.")

    validate_hmac_tag(package.tag)

    return package


def validate_ca_rule_table(rule_table: Any) -> List[int]:
    """Validates Keyed Dynamic Cellular Automata rule lookup table (256 entries, range 0..255).

    Returns:
        Validated rule table as list of integers.

    Raises:
        CryptoError: If rule table is invalid.
    """
    if rule_table is None:
        raise CryptoError("CA rule table cannot be None.")

    if not isinstance(rule_table, (list, tuple, bytes, bytearray)):
        raise CryptoError(f"Invalid CA rule table type '{type(rule_table).__name__}'.")

    rules = list(rule_table)
    if len(rules) != 256:
        raise CryptoError(f"Invalid CA rule table length {len(rules)}. Expected exactly 256 rule entries.")

    for idx, rule in enumerate(rules):
        if not isinstance(rule, int) or rule < 0 or rule > 255:
            raise CryptoError(f"Invalid CA rule entry at index {idx}: {rule}. Must be integer in range [0, 255].")

    return rules


def validate_hmac_tag(tag: Any, expected_length: int = HMAC_TAG_LENGTH) -> bytes:
    """Validates HMAC authentication tag type and byte length.

    Returns:
        Validated tag as bytes.

    Raises:
        CorruptedPayloadError / CryptoError: If tag is None, not bytes-like, or incorrect length.
    """
    if tag is None:
        raise CorruptedPayloadError("HMAC authentication tag cannot be None.")

    if not isinstance(tag, (bytes, bytearray)):
        raise CorruptedPayloadError(f"Invalid HMAC tag type '{type(tag).__name__}'. Expected bytes or bytearray.")

    tag_bytes = bytes(tag)
    if len(tag_bytes) != expected_length:
        raise CorruptedPayloadError(f"Invalid HMAC tag length {len(tag_bytes)} bytes. Expected exactly {expected_length} bytes.")

    return tag_bytes


def validate_hkdf_parameters(
    ikm: Any,
    salt: Any,
    info: Any,
    length: int
) -> Dict[str, Any]:
    """Validates HKDF expansion input parameters.

    Returns:
        Validated parameter dictionary.

    Raises:
        KeyDerivationError: If HKDF arguments violate RFC 5869 constraints.
    """
    if ikm is None or not isinstance(ikm, (bytes, bytearray)) or len(ikm) == 0:
        raise KeyDerivationError("Input Keying Material (IKM) must be a non-empty bytes-like buffer.")

    if salt is not None and not isinstance(salt, (bytes, bytearray)):
        raise KeyDerivationError("HKDF salt must be bytes, bytearray, or None.")

    if info is not None and not isinstance(info, (bytes, bytearray, str)):
        raise KeyDerivationError("HKDF info string must be bytes, bytearray, str, or None.")

    if not isinstance(length, int) or length <= 0 or length > HKDF_MAX_OUTPUT:
        raise KeyDerivationError(f"Invalid HKDF output length {length}. Must be integer in range 1..{HKDF_MAX_OUTPUT}.")

    return {
        "ikm_bytes": bytes(ikm),
        "salt_bytes": bytes(salt) if salt is not None else b"",
        "info_bytes": info.encode("utf-8") if isinstance(info, str) else (bytes(info) if info is not None else b""),
        "requested_length": length,
    }


def run_comprehensive_system_validation() -> Dict[str, Any]:
    """Executes system-wide validation checks across all component inputs and boundary conditions.

    Returns:
        Summary dictionary of system validation checks.
    """
    checks = []

    # Check 1: Master Key Validation
    try:
        _ = validate_master_key(b"Master_Key_256_Bits_Validation!")
        checks.append({"check": "Master Key Validation", "status": "PASS"})
    except Exception as err:
        checks.append({"check": "Master Key Validation", "status": "FAIL", "error": str(err)})

    # Check 2: Salt & Nonce Validation
    try:
        _ = validate_salt(b"\x00" * 16)
        _ = validate_nonce(b"\x01" * 12)
        checks.append({"check": "Salt & Nonce Validation", "status": "PASS"})
    except Exception as err:
        checks.append({"check": "Salt & Nonce Validation", "status": "FAIL", "error": str(err)})

    # Check 3: Payload Data Validation
    try:
        _ = validate_payload_data(b"Sample payload buffer")
        checks.append({"check": "Payload Data Validation", "status": "PASS"})
    except Exception as err:
        checks.append({"check": "Payload Data Validation", "status": "FAIL", "error": str(err)})

    # Check 4: Encrypted Package Validation
    try:
        pkg = EncryptedPackage("1.0.0", b"\x10" * 16, b"\x20" * 12, b"ciphertext_bytes", b"\x30" * 32)
        _ = validate_encrypted_package(pkg)
        checks.append({"check": "Encrypted Package Validation", "status": "PASS"})
    except Exception as err:
        checks.append({"check": "Encrypted Package Validation", "status": "FAIL", "error": str(err)})

    # Check 5: CA Rule Table Validation
    try:
        _ = validate_ca_rule_table(list(range(256)))
        checks.append({"check": "CA Rule Table Validation", "status": "PASS"})
    except Exception as err:
        checks.append({"check": "CA Rule Table Validation", "status": "FAIL", "error": str(err)})

    # Check 6: HKDF Parameter Validation
    try:
        _ = validate_hkdf_parameters(b"ikm_bytes", b"salt", b"info", 32)
        checks.append({"check": "HKDF Parameter Validation", "status": "PASS"})
    except Exception as err:
        checks.append({"check": "HKDF Parameter Validation", "status": "FAIL", "error": str(err)})

    all_passed = all(c["status"] == "PASS" for c in checks)

    return {
        "total_checks": len(checks),
        "passed": sum(1 for c in checks if c["status"] == "PASS"),
        "failed": sum(1 for c in checks if c["status"] == "FAIL"),
        "checks": checks,
        "overall_status": "PASS" if all_passed else "FAIL",
    }
