"""
Custom Cryptographic Exceptions Hierarchy.

IEEE Mapping: Section IV-D (Fault & Error Handling)
"""


class CryptoError(Exception):
    """Base exception for all cryptographic errors."""
    pass


class AuthenticationError(CryptoError):
    """Raised when HMAC authentication tag verification fails."""
    pass


class KeyDerivationError(CryptoError):
    """Raised when key derivation inputs or operations fail."""
    pass


class CorruptedPayloadError(CryptoError):
    """Raised when payload schema or byte alignment is invalid."""
    pass
