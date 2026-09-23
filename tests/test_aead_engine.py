"""Unit tests for AEADEngine (crypto/primitives/aead.py)."""

import pytest
from crypto.primitives.aead import AEADEngine
from crypto.primitives.auth import AEADAuthenticationError
from crypto.primitives.nonce import NonceReuseError


class TestAEADEngine:
    """Tests for AEADEngine authenticated encryption, decryption, AAD, and failure handling."""

    def test_encrypt_decrypt_roundtrip(self):
        """Verify AEAD encryption and decryption roundtrip."""
        engine = AEADEngine()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Sensitive Payload Message to Encrypt"
        aad = b"header_context_info"

        res = engine.encrypt(plaintext, master_key=master_key, aad=aad, tag_length=16)
        assert "ciphertext" in res
        assert "tag" in res
        assert "nonce" in res
        assert len(res["tag"]) == 16
        assert len(res["nonce"]) == 12

        # Decrypt
        decrypted = engine.decrypt(
            ciphertext=res["ciphertext"],
            tag=res["tag"],
            master_key=master_key,
            nonce=res["nonce"],
            aad=aad,
        )
        assert decrypted == plaintext

    test_byteslike_types = [
        b"Binary bytes plaintext",
        bytearray(b"Bytearray plaintext"),
        memoryview(b"Memoryview plaintext"),
    ]

    @pytest.mark.parametrize("pt_input", test_byteslike_types)
    def test_byteslike_inputs(self, pt_input):
        """Verify AEADEngine accepts bytes, bytearray, and memoryview objects."""
        engine = AEADEngine()
        master_key = b"master_key_bytes_123456789012345"

        res = engine.encrypt(pt_input, master_key=master_key, check_nonce_reuse=False)
        decrypted = engine.decrypt(res["ciphertext"], res["tag"], master_key, res["nonce"])

        if isinstance(pt_input, memoryview):
            expected = pt_input.tobytes()
        else:
            expected = bytes(pt_input)

        assert decrypted == expected

    def test_corrupted_ciphertext_raises_error(self):
        """Verify tampering with ciphertext triggers uniform AEADAuthenticationError."""
        engine = AEADEngine()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Test Payload"

        res = engine.encrypt(plaintext, master_key=master_key)
        ct_tampered = bytearray(res["ciphertext"])
        ct_tampered[0] ^= 0xFF

        with pytest.raises(AEADAuthenticationError, match="AEAD authentication failed"):
            engine.decrypt(bytes(ct_tampered), res["tag"], master_key, res["nonce"])

    def test_corrupted_aad_raises_error(self):
        """Verify tampering with AAD triggers uniform AEADAuthenticationError."""
        engine = AEADEngine()
        master_key = b"master_key_bytes_123456789012345"
        plaintext = b"Test Payload"
        aad = b"original_aad"

        res = engine.encrypt(plaintext, master_key=master_key, aad=aad)

        with pytest.raises(AEADAuthenticationError, match="AEAD authentication failed"):
            engine.decrypt(res["ciphertext"], res["tag"], master_key, res["nonce"], aad=b"tampered_aad")

    def test_nonce_reuse_prevention(self):
        """Verify attempting to reuse explicit nonce triggers NonceReuseError."""
        engine = AEADEngine()
        master_key = b"master_key_bytes_123456789012345"
        nonce = b"explicit_12B"

        engine.encrypt(b"Payload 1", master_key=master_key, nonce=nonce, check_nonce_reuse=True)

        with pytest.raises(NonceReuseError):
            engine.encrypt(b"Payload 2", master_key=master_key, nonce=nonce, check_nonce_reuse=True)
