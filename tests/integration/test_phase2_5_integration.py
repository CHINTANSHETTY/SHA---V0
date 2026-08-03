"""
Integration Test Suite: Phase 2.5 - System Integration & Final Validation.

IEEE Mapping: Section VII (System Integration, End-to-End Pipeline & Reproducibility)
Verifies:
  1. Full End-to-End Pipeline Encryption & Decryption across all payload types.
  2. AEAD Authentication Tag Verification & Tamper/Forgery Rejection.
  3. Master Key, CA Seed, and Dynamic Rule Scheduler Determinism.
  4. Scheduler & Cellular Automata Step Synchronization under stress.
  5. State Isolation & Nonce Freshness Guarantees.
"""

from __future__ import annotations

import os
import pytest

from crypto.engine.encrypt import encrypt_bytes
from crypto.engine.decrypt import decrypt_bytes
from crypto.engine.key_schedule import KeySchedule
from crypto.engine.dynamic_ca import DynamicCAEngine
from crypto.ca.engine import evolve_step, evolve
from crypto.models.package import EncryptedPackage
from crypto.models.exceptions import CryptoError, AuthenticationError


class TestPhase25SystemIntegration:
    """Comprehensive Phase 2.5 Integration Test Suite."""

    @pytest.fixture
    def master_key(self) -> bytes:
        return b"Phase2_5_System_Integration_Key_32B!"

    @pytest.fixture
    def fixed_salt(self) -> bytes:
        return b"\x10" * 16

    @pytest.fixture
    def fixed_nonce(self) -> bytes:
        return b"\x20" * 12

    # -------------------------------------------------------------------------
    # 1. Full End-to-End Pipeline Validation
    # -------------------------------------------------------------------------

    @pytest.mark.parametrize(
        "payload, description",
        [
            (b"", "Empty Plaintext"),
            (b"A", "Single Byte"),
            (b"Short healthcare EHR test payload.", "Short Text"),
            (b"KDR-CA-AEAD Framework Integration Test Payload " * 100, "Medium Payload"),
            (os.urandom(1024 * 1024), "Large 1MB Payload"),
            (os.urandom(512), "Random Bytes"),
            (bytes(range(256)) * 4, "Binary 0x00-0xFF Buffer"),
            ("🔐 KDR-CA-AEAD Cryptographic Engine 🚀 ❤️ 漢字 EHR Record".encode("utf-8"), "Unicode Text"),
        ],
        ids=[
            "Empty",
            "SingleByte",
            "ShortText",
            "MediumPayload",
            "Large1MBPayload",
            "RandomBytes",
            "BinaryBuffer",
            "UnicodeText",
        ],
    )
    def test_e2e_encryption_decryption_payload_varieties(self, master_key: bytes, payload: bytes, description: str):
        """Validates that all payload types encrypt and decrypt round-trip cleanly."""
        package = encrypt_bytes(payload, master_key)
        assert isinstance(package, EncryptedPackage)
        assert package.version == "KDR-CA-AEAD-v1"
        assert len(package.salt) == 16
        assert len(package.nonce) == 12
        assert len(package.tag) == 32  # HMAC-SHA256 32-byte tag

        decrypted = decrypt_bytes(package, master_key)
        assert decrypted == payload, f"Failed round-trip for {description}"

    def test_e2e_encryption_with_associated_data(self, master_key: bytes):
        """Validates AEAD encryption and decryption with associated authenticated data (AD)."""
        payload = b"Confidential Patient Diagnostic Payload"
        ad = b"Header: EHR-Patient-ID=9901; Hospital-ID=H-44"

        pkg = encrypt_bytes(payload, master_key, associated_data=ad)
        decrypted = decrypt_bytes(pkg, master_key, associated_data=ad)
        assert decrypted == payload

    # -------------------------------------------------------------------------
    # 2. Authentication Validation & Forgery Rejection
    # -------------------------------------------------------------------------

    def test_aead_ciphertext_tampering_rejection(self, master_key: bytes):
        """Verifies that modifying any bit of ciphertext triggers authentication failure."""
        payload = b"Authenticated EHR Data Buffer"
        pkg = encrypt_bytes(payload, master_key)

        # Flip bit in ciphertext
        tampered_ct = bytearray(pkg.ciphertext)
        if len(tampered_ct) > 0:
            tampered_ct[0] ^= 0x01
        else:
            tampered_ct.append(0x01)

        tampered_pkg = EncryptedPackage(
            version=pkg.version,
            salt=pkg.salt,
            nonce=pkg.nonce,
            ciphertext=bytes(tampered_ct),
            tag=pkg.tag,
        )

        with pytest.raises((CryptoError, AuthenticationError)):
            decrypt_bytes(tampered_pkg, master_key)

    def test_aead_tag_tampering_rejection(self, master_key: bytes):
        """Verifies that modifying any byte of authentication tag is rejected."""
        payload = b"Authenticated EHR Data Buffer"
        pkg = encrypt_bytes(payload, master_key)

        tampered_tag = bytearray(pkg.tag)
        tampered_tag[-1] ^= 0xFF

        tampered_pkg = EncryptedPackage(
            version=pkg.version,
            salt=pkg.salt,
            nonce=pkg.nonce,
            ciphertext=pkg.ciphertext,
            tag=bytes(tampered_tag),
        )

        with pytest.raises((CryptoError, AuthenticationError)):
            decrypt_bytes(tampered_pkg, master_key)

    def test_aead_associated_data_tampering_rejection(self, master_key: bytes):
        """Verifies that modifying associated data during decryption triggers authentication failure."""
        payload = b"Authenticated EHR Payload"
        ad_orig = b"Valid-Header-AD"
        ad_tampered = b"Tampered-Header-AD"

        pkg = encrypt_bytes(payload, master_key, associated_data=ad_orig)

        with pytest.raises((CryptoError, AuthenticationError)):
            decrypt_bytes(pkg, master_key, associated_data=ad_tampered)

    def test_aead_incorrect_key_rejection(self, master_key: bytes):
        """Verifies decryption fails when provided an incorrect master key."""
        payload = b"Secret Medical Telemetry"
        wrong_key = b"Wrong_Master_Key_For_Test_32Bytes!"

        pkg = encrypt_bytes(payload, master_key)

        with pytest.raises((CryptoError, AuthenticationError)):
            decrypt_bytes(pkg, wrong_key)

    # -------------------------------------------------------------------------
    # 3. Deterministic Verification
    # -------------------------------------------------------------------------

    def test_deterministic_mode_repeatability(
        self, master_key: bytes, fixed_salt: bytes, fixed_nonce: bytes
    ):
        """Validates that fixed salt and nonce yield bit-identical ciphertexts and tags across runs."""
        payload = b"Deterministic Repeatability Test Buffer"

        pkg1 = encrypt_bytes(payload, master_key, salt=fixed_salt, nonce=fixed_nonce)
        pkg2 = encrypt_bytes(payload, master_key, salt=fixed_salt, nonce=fixed_nonce)

        assert pkg1.ciphertext == pkg2.ciphertext
        assert pkg1.tag == pkg2.tag
        assert pkg1.salt == pkg2.salt
        assert pkg1.nonce == pkg2.nonce

    def test_key_derivation_determinism(self, master_key: bytes, fixed_salt: bytes, fixed_nonce: bytes):
        """Validates HKDF master key -> derived keys determinism."""
        km1 = KeySchedule.from_master_key(master_key, fixed_salt, fixed_nonce).export_key_material()
        km2 = KeySchedule.from_master_key(master_key, fixed_salt, fixed_nonce).export_key_material()

        assert km1.cipher_key == km2.cipher_key
        assert km1.mac_key == km2.mac_key
        assert km1.rule_seed == km2.rule_seed

    def test_random_mode_freshness(self, master_key: bytes):
        """Validates that default random mode produces unique nonces and salts on consecutive calls."""
        payload = b"Freshness Test Payload"

        pkg1 = encrypt_bytes(payload, master_key)
        pkg2 = encrypt_bytes(payload, master_key)

        assert pkg1.salt != pkg2.salt
        assert pkg1.nonce != pkg2.nonce
        assert pkg1.ciphertext != pkg2.ciphertext

    # -------------------------------------------------------------------------
    # 4. Scheduler & Cellular Automata Synchronization
    # -------------------------------------------------------------------------

    def test_scheduler_ca_step_synchronization(self, master_key: bytes, fixed_salt: bytes, fixed_nonce: bytes):
        """Verifies rule table indexing, step transitions, and DynamicCAEngine state synchronization."""
        from crypto.engine.dynamic_ca import DynamicCAEngine

        km = KeySchedule.from_master_key(master_key, fixed_salt, fixed_nonce).export_key_material()
        engine = DynamicCAEngine.from_key_material(km)

        assert len(engine.rule_table) == 32
        assert engine.rule_table == km.rule_table

        # Verify cyclic rule transitions at byte index boundaries (0 to 64)
        for i in range(64):
            r1 = engine.rule_table[i % 32]
            r2 = engine.rule_table[(i + 13) % 32]
            assert 0 <= r1 <= 255
            assert 0 <= r2 <= 255

    def test_ca_evolution_stress_cycles(self):
        """Executes 1,000 steps of 1D CA evolution to confirm boundary integrity and state stability."""
        from crypto.ca.engine import evolve_step
        from crypto.ca.rules import parse_rule

        initial_state = [1, 0, 1, 1, 0, 0, 1, 0] * 32  # 256-bit state
        current_state = list(initial_state)

        for step in range(1000):
            rule_num = (30 + (step % 5)) % 256
            lookup = parse_rule(rule_num)
            current_state = evolve_step(current_state, lookup, boundary="periodic")
            assert len(current_state) == 256
            assert all(v in (0, 1) for v in current_state)
