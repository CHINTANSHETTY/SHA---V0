"""
Custom Exception Classes for Key Expansion Module.
"""


class KeyExpansionError(Exception):
    """Base exception class for key expansion and derivation errors."""
    pass


class InvalidKeyError(KeyExpansionError, ValueError):
    """Raised when an invalid secret key, key format, or encoding is supplied."""
    pass


class InvalidKeySizeError(KeyExpansionError, ValueError):
    """Raised when an invalid key size or length parameter is requested."""
    pass


class KeyDerivationError(KeyExpansionError, ValueError):
    """Raised when an error occurs during cryptographic byte derivation."""
    pass
