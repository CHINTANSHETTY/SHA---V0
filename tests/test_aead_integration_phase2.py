"""End-to-End Integration Tests & Property Invariants for Phase 2.3 AEAD Subsystem.

Validates end-to-end interactions between:
- AEADEngine
- KeyEvolutionEngine (Phase 2.2)
- DynamicEvolutionEngine (Phase 2.1)
- NonceManager & AuthenticationTag
"""

import pytest
from crypto.key.evolution import KeyEvolutionEngine
from crypto.primitives.aead import AEADEngine
from crypto.primitives.auth import AEADAuthenticationError
from crypto.primitives.nonce import NonceManager, NonceReuseError


class TestPhase23AEADIntegration:
    """Integration and invariant test suite for AEAD Engine."""

    def test_deterministic_reproducibility_invariant(self):
        """Property Invariant: Identical inputs and explicit nonce produce 100% identical ciphertext and tag."""
        engine1 = AEADEngine()
        engine2 = AEADEngine()

        master_key = b"master_key_bytes_reproducible_01"
        plaintext = b"Deterministic payload text"
        aad = b"header_context_v1"
        nonce = b"explicit_12B"

        res1 = engine1.encrypt(plaintext, master_key, aad=aad, nonce=nonce, check_nonce_reuse=False)
        res2 = engine2.encrypt(plaintext, master_key, aad=aad, nonce=nonce, check_nonce_reuse=False)

        assert res1["ciphertext"] == res2["ciphertext"]
        assert res1["tag"] == res2["tag"]

    def test_aad_sensitivity_invariant(self):
        """Property Invariant: Changing only AAD invalidates decryption."""
        engine = AEADEngine()
        master_key = b"master_key_bytes_aad_sensitivity"
        plaintext = b"Sensitive Data"
        aad_correct = b"aad_v1"
        aad_tampered = b"aad_v2"

        res = engine.encrypt(plaintext, master_key, aad=aad_correct, check_nonce_reuse=False)

        with pytest.raises(AEADAuthenticationError):
            engine.decrypt(res["ciphertext"], res["tag"], master_key, res["nonce"], aad=aad_tampered)

    def test_nonce_sensitivity_invariant(self):
        """Property Invariant: Changing only nonce invalidates decryption."""
        engine = AEADEngine()
        master_key = b"master_key_bytes_nonce_sensitivity"
        plaintext = b"Sensitive Data"

        res = engine.encrypt(plaintext, master_key, check_nonce_reuse=False)
        tampered_nonce = bytearray(res["nonce"])
        tampered_nonce[0] ^= 0xFF

        with pytest.raises(AEADAuthenticationError):
            engine.decrypt(res["ciphertext"], res["tag"], master_key, bytes(tampered_nonce))

    def test_key_sensitivity_invariant(self):
        """Property Invariant: Changing master key invalidates decryption."""
        engine = AEADEngine()
        m1 = b"master_key_bytes_original_111111"
        m2 = b"master_key_bytes_tampered_222222"
        plaintext = b"Sensitive Data"

        res = engine.encrypt(plaintext, master_key=m1, check_nonce_reuse=False)

        with pytest.raises(AEADAuthenticationError):
            engine.decrypt(res["ciphertext"], res["tag"], master_key=m2, nonce=res["nonce"])

    def test_replay_protection_invariant(self):
        """Property Invariant: Replaying registered nonce raises NonceReuseError."""
        engine = AEADEngine()
        master_key = b"master_key_bytes_replay_test_1"
        nonce = b"replay_nonce"

        engine.encrypt(b"Payload 1", master_key=master_key, nonce=nonce, check_nonce_reuse=True)

        with pytest.raises(NonceReuseError):
            engine.encrypt(b"Payload 2", master_key=master_key, nonce=nonce, check_nonce_reuse=True)
