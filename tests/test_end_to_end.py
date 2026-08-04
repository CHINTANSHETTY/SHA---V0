"""
Phase 4.1 End-to-End Workflow & Determinism Tests (`tests/test_end_to_end.py`).

Verifies end-to-end encryption/decryption, streaming AEAD, serialization, determinism,
large payloads, and security error handling.
"""

import io
import json
import pytest

from crypto import (
    encrypt_bytes,
    encrypt_payload,
    decrypt_bytes,
    decrypt_payload,
    EncryptedPackage,
    KeySchedule,
    StreamingAEAD,
    CryptoError,
    AuthenticationError,
)
from crypto.models.exceptions import CorruptedPayloadError
from crypto.primitives.streaming import StreamCorruptedError


class TestEndToEndLifecycle:
    """Verifies complete end-to-end encryption and authenticated decryption workflows."""

    def test_bytes_encryption_decryption_lifecycle(self) -> None:
        """Verify byte buffer encryption and decryption round-trip."""
        master_key = b"master_key_bytes_e2e_32bytes_!!"
        plaintext = b"End-to-End Byte Encryption Test Payload \x00\x01\x02\xff" * 10
        salt = b"1234567890abcdef"
        nonce = b"12byte_nonce"
        ad = b"associated_data_header"

        pkg = encrypt_bytes(plaintext, master_key, salt=salt, nonce=nonce, associated_data=ad)

        assert isinstance(pkg, EncryptedPackage)
        assert pkg.salt == salt
        assert pkg.nonce == nonce
        assert len(pkg.ciphertext) == len(plaintext)
        assert len(pkg.tag) == 32

        decrypted = decrypt_bytes(pkg, master_key, associated_data=ad)
        assert decrypted == plaintext

    def test_payload_string_encryption_decryption_lifecycle(self) -> None:
        """Verify string payload encryption and decryption round-trip."""
        password = "SecureUserPassword!2026"
        plaintext = "High-level payload string testing KDR-CA-AEAD 🔐"
        salt = b"salt16bytes_repr"
        nonce = b"nonce12bytes"

        pkg = encrypt_payload(plaintext, password, salt=salt, nonce=nonce)
        decrypted = decrypt_payload(pkg, password)

        assert decrypted == plaintext

    def test_streaming_encryption_decryption_lifecycle(self) -> None:
        """Verify streaming AEAD chunked encryption/decryption round-trip."""
        streaming = StreamingAEAD()
        master_key = b"streaming_master_key_32bytes_ok"
        nonce = b"streamnonce1"
        aad = b"stream_aad_header"
        data = b"Arbitrary streaming chunk content for test " * 2000

        in_stream = io.BytesIO(data)
        out_stream = io.BytesIO()

        enc_res = streaming.encrypt_stream(in_stream, out_stream, master_key, nonce=nonce, aad=aad, chunk_size=4096)
        assert enc_res["total_bytes"] == len(data)

        out_stream.seek(0)
        dec_stream = io.BytesIO()
        dec_res = streaming.decrypt_stream(out_stream, dec_stream, master_key, aad=aad)

        assert dec_res["total_bytes"] == len(data)
        assert dec_stream.getvalue() == data


class TestDeterminismAndRegression:
    """Verifies output equality and determinism across repeated executions."""

    def test_deterministic_outputs(self) -> None:
        """Verify identical outputs for identical keys, salts, nonces, and inputs."""
        master_key = b"deterministic_test_key_32bytes!"
        salt = b"fixed_salt_16byte"[:16]
        nonce = b"12byte_nonce"
        plaintext = b"Deterministic payload content verification"

        pkg1 = encrypt_bytes(plaintext, master_key, salt=salt, nonce=nonce)
        pkg2 = encrypt_bytes(plaintext, master_key, salt=salt, nonce=nonce)

        assert pkg1.salt == pkg2.salt
        assert pkg1.nonce == pkg2.nonce
        assert pkg1.ciphertext == pkg2.ciphertext
        assert pkg1.tag == pkg2.tag

        ks1 = KeySchedule.from_master_key(master_key, salt, nonce).export_key_material()
        ks2 = KeySchedule.from_master_key(master_key, salt, nonce).export_key_material()

        assert ks1.cipher_key == ks2.cipher_key
        assert ks1.mac_key == ks2.mac_key
        assert ks1.rule_table == ks2.rule_table


class TestSerializationCompatibility:
    """Verifies format specification and serialization compatibility for EncryptedPackage."""

    def test_encrypted_package_to_from_dict(self) -> None:
        """Verify EncryptedPackage hex dictionary serialization."""
        pkg = EncryptedPackage(
            version="1.0.0",
            salt=b"salt_16_bytes_ok",
            nonce=b"nonce_12byte",
            ciphertext=b"ciphertext_bytes_here",
            tag=b"tag_32_bytes_hmac_sha256_result!",
        )

        d = pkg.to_dict()
        assert d["version"] == "1.0.0"
        assert d["salt"] == pkg.salt.hex()
        assert d["nonce"] == pkg.nonce.hex()
        assert d["ciphertext"] == pkg.ciphertext.hex()
        assert d["tag"] == pkg.tag.hex()

        restored = EncryptedPackage.from_dict(d)
        assert restored == pkg

    def test_encrypted_package_to_from_json(self) -> None:
        """Verify EncryptedPackage JSON string serialization."""
        pkg = EncryptedPackage(
            version="1.0.0",
            salt=b"salt_16_bytes_ok",
            nonce=b"nonce_12byte",
            ciphertext=b"ciphertext_bytes_here",
            tag=b"tag_32_bytes_hmac_sha256_result!",
        )

        json_str = pkg.to_json()
        assert isinstance(json_str, str)

        restored = EncryptedPackage.from_json(json_str)
        assert restored == pkg

    def test_malformed_package_deserialization(self) -> None:
        """Verify error handling on malformed JSON or dict inputs."""
        with pytest.raises(CorruptedPayloadError):
            EncryptedPackage.from_dict({"version": "1.0.0", "salt": "1234"})

        with pytest.raises(CorruptedPayloadError):
            EncryptedPackage.from_json("invalid json string")


class TestLargePayloadsAndErrors:
    """Verifies handling of multi-megabyte payloads and error paths."""

    def test_large_payload_e2e(self) -> None:
        """Verify end-to-end encryption/decryption of a 2MB binary buffer."""
        master_key = b"large_payload_master_key_32bytes"
        large_buf = bytes((i % 256) for i in range(2 * 1024 * 1024))

        pkg = encrypt_bytes(large_buf, master_key)
        assert len(pkg.ciphertext) == len(large_buf)

        decrypted = decrypt_bytes(pkg, master_key)
        assert decrypted == large_buf

    def test_corrupted_ciphertext_raises_authentication_error(self) -> None:
        """Verify payload tampered in transit raises AuthenticationError."""
        master_key = b"corrupted_ct_key_32bytes_check!"
        plaintext = b"Sensitive payload needing integrity protection"

        pkg = encrypt_bytes(plaintext, master_key)
        corrupted_ct = bytearray(pkg.ciphertext)
        corrupted_ct[0] ^= 0xFF

        bad_pkg = EncryptedPackage(
            version=pkg.version,
            salt=pkg.salt,
            nonce=pkg.nonce,
            ciphertext=bytes(corrupted_ct),
            tag=pkg.tag,
        )

        with pytest.raises(AuthenticationError):
            decrypt_bytes(bad_pkg, master_key)

    def test_invalid_password_raises_authentication_error(self) -> None:
        """Verify incorrect decryption password fails authentication."""
        pkg = encrypt_payload("Secret Message", "CorrectPassword123")
        with pytest.raises(AuthenticationError):
            decrypt_payload(pkg, "WrongPassword123")

    def test_stream_tampering_raises_stream_corrupted_error(self) -> None:
        """Verify stream tampering or invalid header raises StreamCorruptedError."""
        streaming = StreamingAEAD()
        master_key = b"stream_tamper_key_32bytes_check"
        data = b"Stream content for corruption testing"

        in_stream = io.BytesIO(data)
        out_stream = io.BytesIO()
        streaming.encrypt_stream(in_stream, out_stream, master_key, nonce=b"12byte_nonce")

        corrupted_stream = bytearray(out_stream.getvalue())
        corrupted_stream[0] = ord('X')  # Corrupt header magic

        with pytest.raises(StreamCorruptedError):
            streaming.decrypt_stream(io.BytesIO(corrupted_stream), io.BytesIO(), master_key)
