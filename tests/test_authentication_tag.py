"""Unit tests for AuthenticationTag (crypto/primitives/auth.py)."""

import pytest
from crypto.primitives.auth import (
    AEADAuthenticationError,
    AuthenticationTag,
    InvalidTagError,
)


class TestAuthenticationTag:
    """Tests for AuthenticationTag canonical framing and constant-time verification."""

    def test_generate_and_verify_tag(self):
        """Verify tag generation and verification roundtrip."""
        auth_key = b"auth_key_bytes_1234567890123456"
        ciphertext = b"encrypted_payload_bytes"
        nonce = b"nonce_12bytes"
        aad = b"associated_data_header"

        tag = AuthenticationTag.generate(auth_key, ciphertext, nonce, aad, tag_length=16)
        assert len(tag) == 16

        # Verification succeeds
        assert AuthenticationTag.verify(auth_key, ciphertext, nonce, tag, aad) is True

    def test_32byte_research_tag(self):
        """Verify 32-byte research full HMAC tag."""
        auth_key = b"auth_key_bytes_1234567890123456"
        ciphertext = b"payload"
        nonce = b"nonce_12bytes"

        tag32 = AuthenticationTag.generate(auth_key, ciphertext, nonce, tag_length=32)
        assert len(tag32) == 32
        assert AuthenticationTag.verify(auth_key, ciphertext, nonce, tag32) is True

    def test_tampered_ciphertext_fails_verification(self):
        """Verify modifying ciphertext causes uniform AEADAuthenticationError."""
        auth_key = b"auth_key_bytes_1234567890123456"
        ciphertext = b"encrypted_payload_bytes"
        nonce = b"nonce_12bytes"

        tag = AuthenticationTag.generate(auth_key, ciphertext, nonce)
        tampered_ct = b"encrypted_payload_byteX"

        with pytest.raises(AEADAuthenticationError, match="Authentication verification failed"):
            AuthenticationTag.verify(auth_key, tampered_ct, nonce, tag)

    def test_tampered_aad_fails_verification(self):
        """Verify modifying AAD causes uniform AEADAuthenticationError."""
        auth_key = b"auth_key_bytes_1234567890123456"
        ciphertext = b"encrypted_payload_bytes"
        nonce = b"nonce_12bytes"
        aad = b"header_v1"

        tag = AuthenticationTag.generate(auth_key, ciphertext, nonce, aad=aad)

        with pytest.raises(AEADAuthenticationError, match="Authentication verification failed"):
            AuthenticationTag.verify(auth_key, ciphertext, nonce, tag, aad=b"header_v2")

    def test_constant_time_compare(self):
        """Verify constant-time tag comparison utility."""
        tag1 = b"0123456789abcdef"
        tag2 = b"0123456789abcdef"
        tag3 = b"0123456789abcdeg"

        assert AuthenticationTag.compare(tag1, tag2) is True
        assert AuthenticationTag.compare(tag1, tag3) is False
