"""Unit tests for StreamingAEAD (crypto/primitives/streaming.py)."""

import io
import pytest
from crypto.primitives.streaming import StreamCorruptedError, StreamingAEAD


class TestStreamingAEAD:
    """Tests for StreamingAEAD file/stream encryption, chunk ordering, and tampering rejection."""

    def test_stream_encryption_decryption_roundtrip(self):
        """Verify streaming encryption and decryption roundtrip over in-memory BytesIO streams."""
        engine = StreamingAEAD()
        master_key = b"master_key_bytes_123456789012345"
        nonce = b"nonce_12bytes"
        aad = b"header_metadata"

        plaintext = b"Hello World! " * 5000  # ~65 KB payload
        in_stream = io.BytesIO(plaintext)
        enc_stream = io.BytesIO()

        res_enc = engine.encrypt_stream(
            in_stream,
            enc_stream,
            master_key=master_key,
            nonce=nonce,
            aad=aad,
            chunk_size=16384,  # 16 KB chunks
        )
        assert res_enc["total_bytes"] == len(plaintext)
        assert res_enc["chunk_count"] > 1

        # Decrypt
        enc_stream.seek(0)
        out_stream = io.BytesIO()
        res_dec = engine.decrypt_stream(enc_stream, out_stream, master_key=master_key, aad=aad)

        assert res_dec["total_bytes"] == len(plaintext)
        assert out_stream.getvalue() == plaintext

    def test_corrupted_header_raises_error(self):
        """Verify invalid or corrupted stream header magic raises StreamCorruptedError."""
        engine = StreamingAEAD()
        master_key = b"master_key_bytes_123456789012345"

        bad_stream = io.BytesIO(b"BADHEADER_payload_bytes_123456789")
        out_stream = io.BytesIO()

        with pytest.raises(StreamCorruptedError, match="Invalid or corrupted stream header"):
            engine.decrypt_stream(bad_stream, out_stream, master_key=master_key)

    def test_tampered_chunk_payload_raises_error(self):
        """Verify modifying chunk bytes triggers StreamCorruptedError during tag verification."""
        engine = StreamingAEAD()
        master_key = b"master_key_bytes_123456789012345"
        nonce = b"nonce_12bytes"

        in_stream = io.BytesIO(b"Data to be encrypted")
        enc_stream = io.BytesIO()

        engine.encrypt_stream(in_stream, enc_stream, master_key=master_key, nonce=nonce)

        # Flip a bit in the encrypted stream content
        raw = bytearray(enc_stream.getvalue())
        raw[25] ^= 0xFF
        tampered_stream = io.BytesIO(bytes(raw))
        out_stream = io.BytesIO()

        with pytest.raises(StreamCorruptedError):
            engine.decrypt_stream(tampered_stream, out_stream, master_key=master_key)
