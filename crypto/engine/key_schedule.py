"""
Module:
    key_schedule.py

Project:
    KDR-CA-AEAD

Purpose:
    Implements domain-separated dynamic sub-key expansion for Cellular Automata rules,
    cipher keystream, and HMAC authentication tags.

Author:
    Chintan

Version:
    1.0.0

IEEE Mapping:
    Section IV-B – Dynamic Sub-Key Expansion Subsystem

Standards:
    NIST SP 800-56C Rev. 2 – Key-Derivation Methods & Domain Separation
    RFC 5869 – HKDF

Dependencies:
    dataclasses
    typing
    crypto.constants
    crypto.primitives.hkdf
    crypto.models.exceptions

Security Classification:
    Critical Key Management Component
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, TypeAlias

from crypto.constants import DEFAULT_NONCE_LENGTH, DEFAULT_SALT_LENGTH
from crypto.models.exceptions import KeyDerivationError
from crypto.primitives.hkdf import hkdf

__all__ = ["KeySchedule", "KeyMaterial", "BytesLike", "PROTOCOL_VERSION"]

BytesLike: TypeAlias = bytes | bytearray

# =========================================================
# PROTOCOL VERSION & DOMAIN SEPARATION LABELS
# =========================================================
PROTOCOL_VERSION: str = "KDR-CA-AEAD-v1"

LABEL_CA_RULES: bytes = f"{PROTOCOL_VERSION}-ca-rules|".encode()
LABEL_CIPHER_KEY: bytes = f"{PROTOCOL_VERSION}-cipher-key|".encode()
LABEL_MAC_KEY: bytes = f"{PROTOCOL_VERSION}-mac-key|".encode()


@dataclass(frozen=True)
class KeyMaterial:
    """Immutable data container for derived sub-key material.

    Attributes:
        rule_seed: 32-byte seed (K_r) used to derive CA transition rule tables.
        cipher_key: 32-byte key (K_c) for CTR keystream PRNG generation.
        mac_key: 32-byte key (K_a) for HMAC-SHA256 authentication tag computation.
        rule_table: Immutable 32-element tuple of uint8 CA transition rules (0..255).
                    Rationale: 32 rules align directly with the 32-byte (256-bit) rule seed (K_r)
                    derived from SHA-256 HKDF. 1 byte maps to 1 local uint8 rule. For payloads
                    exceeding 32 blocks, rules are applied cyclically: R_{i mod 32}. Future protocol
                    versions may support larger rule tables without altering this public API.
        algorithm_id: Protocol version string identifier for cryptographic traceability.
        metadata: Optional metadata dictionary reserved for future extensions.
    """

    rule_seed: bytes
    cipher_key: bytes
    mac_key: bytes
    rule_table: tuple[int, ...]
    algorithm_id: str = PROTOCOL_VERSION

    @property
    def rule_key(self) -> bytes:
        """Backward-compatible alias for rule_seed."""
        return self.rule_seed


class KeySchedule:
    """Manages dynamic expansion and domain separation of sub-keys (K_r, K_c, K_a).

    Design Rationale - Nonce in HKDF `info`:
        Per RFC 5869 Section 3.2, `IKM` represents high/medium entropy secret material
        (master key), `salt` acts as the extraction randomizer (16-byte CSPRNG salt), and
        `info` binds application and context-specific parameters.
        Placing the 12-byte per-encryption `nonce` into the `info` context string explicitly
        binds each derived sub-key to both the domain function ("ca-rules", "cipher-key", "mac-key")
        and the specific message nonce context during HKDF expansion, ensuring strong per-nonce
        domain separation.
    """

    def __init__(self, master_key: BytesLike, salt: BytesLike, nonce: BytesLike) -> None:
        """Initializes KeySchedule and executes domain-separated HKDF derivations.

        Preconditions:
            - master_key must be a non-empty bytes-like buffer (min 16 bytes recommended).
            - salt must be a bytes-like buffer of exactly 16 bytes.
            - nonce must be a bytes-like buffer of exactly 12 bytes.

        Postconditions:
            - Derives independent 32-byte K_r (rule_seed), 32-byte K_c, and 32-byte K_a sub-keys.
            - Constructs 32 uint8 CA transition rules in rule_table.

        Args:
            master_key: Master key bytes or derived password seed bytes.
            salt: 16-byte random salt buffer.
            nonce: 12-byte random nonce buffer.

        Raises:
            KeyDerivationError: If parameter validation fails.
            TypeError: If input types are not bytes-like buffers.
        """
        self._validate_inputs(master_key, salt, nonce)

        mk_bytes = bytes(master_key)
        salt_bytes = bytes(salt)
        nonce_bytes = bytes(nonce)

        # Execute 3 domain-separated HKDF expansions (RFC 5869 Section 3.2 context binding)
        rule_seed = hkdf(
            ikm=mk_bytes,
            length=32,
            salt=salt_bytes,
            info=LABEL_CA_RULES + nonce_bytes
        )
        cipher_key = hkdf(
            ikm=mk_bytes,
            length=32,
            salt=salt_bytes,
            info=LABEL_CIPHER_KEY + nonce_bytes
        )
        mac_key = hkdf(
            ikm=mk_bytes,
            length=32,
            salt=salt_bytes,
            info=LABEL_MAC_KEY + nonce_bytes
        )

        rule_table = tuple(rule_seed)

        self._key_material = KeyMaterial(
            rule_seed=rule_seed,
            cipher_key=cipher_key,
            mac_key=mac_key,
            rule_table=rule_table,
            algorithm_id=PROTOCOL_VERSION
        )

    @staticmethod
    def _validate_inputs(master_key: BytesLike, salt: BytesLike, nonce: BytesLike) -> None:
        """Validates input types and byte lengths."""
        if not master_key or not isinstance(master_key, (bytes, bytearray)):
            raise KeyDerivationError("Master key must be a non-empty bytes-like object.")

        if len(master_key) < 1:
            raise KeyDerivationError("Master key must contain at least 1 byte.")

        if not salt or not isinstance(salt, (bytes, bytearray)) or len(salt) != DEFAULT_SALT_LENGTH:
            raise KeyDerivationError(f"Salt must be a bytes-like object of exactly {DEFAULT_SALT_LENGTH} bytes.")

        if not nonce or not isinstance(nonce, (bytes, bytearray)) or len(nonce) != DEFAULT_NONCE_LENGTH:
            raise KeyDerivationError(f"Nonce must be a bytes-like object of exactly {DEFAULT_NONCE_LENGTH} bytes.")

    @classmethod
    def from_master_key(
        cls,
        master_key: BytesLike,
        salt: BytesLike,
        nonce: BytesLike
    ) -> KeySchedule:
        """Factory method constructing KeySchedule from master key bytes."""
        return cls(master_key, salt, nonce)

    def export_key_material(self) -> KeyMaterial:
        """Returns immutable KeyMaterial dataclass containing derived sub-keys."""
        return self._key_material

    def get_ca_rule_table(self) -> tuple[int, ...]:
        """Returns immutable tuple of 32 uint8 CA rules."""
        return self._key_material.rule_table

    def get_cipher_key(self) -> bytes:
        """Returns 32-byte cipher key K_c."""
        return self._key_material.cipher_key

    def get_mac_key(self) -> bytes:
        """Returns 32-byte HMAC authentication key K_a."""
        return self._key_material.mac_key
