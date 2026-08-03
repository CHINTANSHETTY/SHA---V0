"""Cryptographic Primitives Subsystem (`crypto.primitives`).

This package provides standard and enhanced cryptographic primitives for the KDR-CA-AEAD system:
1. HKDF-SHA256 (`crypto.primitives.hkdf`): RFC 5869 Extract & Expand key derivation functions.
2. HMAC-SHA256 (`crypto.primitives.hmac`): FIPS 198-1 authentication messaging primitives.
3. CSPRNG (`crypto.primitives.random`): Cryptographically secure random salt and nonce generators.
4. Nonce Manager (`crypto.primitives.nonce`): AEAD nonce generation, validation, and bounded LRU reuse detection (`NonceManager`).
5. Authentication Tag (`crypto.primitives.auth`): Canonical versioned frame tagging and constant-time tag verification (`AuthenticationTag`).
6. Streaming AEAD (`crypto.primitives.streaming`): Chunked file and stream authenticated encryption (`StreamingAEAD`).
7. AEAD Engine (`crypto.primitives.aead`): Enhanced Authenticated Encryption with Associated Data engine (`AEADEngine`).
"""

__version__: str = "2.3.0"
__author__: str = "KDR-CA-AEAD Project"

# =========================================================
# RE-EXPORTS: STANDARD PRIMITIVES (PHASE 1)
# =========================================================
from .hkdf import BytesLike, hkdf, hkdf_expand, hkdf_extract
from .hmac import generate_hmac, verify_hmac
from .random import generate_nonce, generate_salt

# =========================================================
# RE-EXPORTS: ENHANCED AEAD PRIMITIVES & ENGINES (PHASE 2.3)
# =========================================================
from .nonce import (
    DEFAULT_MAX_CAPACITY,
    DEFAULT_NONCE_LENGTH,
    MAX_NONCE_LENGTH,
    MIN_NONCE_LENGTH,
    AEADError,
    InvalidNonceError,
    NonceManager,
    NonceReuseError,
)

from .auth import (
    DEFAULT_TAG_LENGTH,
    FRAME_VERSION,
    FULL_TAG_LENGTH,
    AEADAuthenticationError,
    AuthenticationTag,
    InvalidTagError,
)

from .streaming import (
    DEFAULT_CHUNK_SIZE,
    STREAM_HEADER_MAGIC,
    STREAM_VERSION,
    StreamCorruptedError,
    StreamingAEAD,
    StreamingAEADError,
)

from .aead import AEADEngine

# =========================================================
# EXPLICIT PUBLIC API
# =========================================================
__all__ = [
    # Metadata
    "__version__",
    "__author__",
    # Standard Primitives (Phase 1)
    "BytesLike",
    "hkdf",
    "hkdf_extract",
    "hkdf_expand",
    "generate_hmac",
    "verify_hmac",
    "generate_salt",
    "generate_nonce",
    # Exceptions
    "AEADError",
    "InvalidNonceError",
    "NonceReuseError",
    "AEADAuthenticationError",
    "InvalidTagError",
    "StreamingAEADError",
    "StreamCorruptedError",
    # Constants
    "MIN_NONCE_LENGTH",
    "DEFAULT_NONCE_LENGTH",
    "MAX_NONCE_LENGTH",
    "DEFAULT_MAX_CAPACITY",
    "FRAME_VERSION",
    "DEFAULT_TAG_LENGTH",
    "FULL_TAG_LENGTH",
    "STREAM_HEADER_MAGIC",
    "STREAM_VERSION",
    "DEFAULT_CHUNK_SIZE",
    # Engines & Managers (Phase 2.3)
    "NonceManager",
    "AuthenticationTag",
    "StreamingAEAD",
    "AEADEngine",
]
