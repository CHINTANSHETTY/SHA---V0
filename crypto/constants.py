"""Cryptographic System Constants.

Defines global constants, version numbers, and algorithmic boundaries.
IEEE Mapping: Section IV-A / IV-B
"""

# =========================================================
# HKDF PRIMITIVE CONSTANTS (RFC 5869)
# =========================================================
HKDF_HASH_LENGTH: int = 32          # SHA-256 digest size in bytes
HKDF_MAX_OUTPUT: int = 255 * 32    # 8160 bytes max expansion limit (1-octet counter: 0x01..0xFF)
HKDF_VERSION: str = "1.0.0"

# =========================================================
# HMAC PRIMITIVE CONSTANTS (RFC 2104)
# =========================================================
HMAC_TAG_LENGTH: int = 32          # HMAC-SHA256 tag size in bytes

# =========================================================
# SYSTEM SECURITY CONSTANTS
# =========================================================
DEFAULT_SALT_LENGTH: int = 16       # 128-bit random salt
DEFAULT_NONCE_LENGTH: int = 12      # 96-bit random nonce
