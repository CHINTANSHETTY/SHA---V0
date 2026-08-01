"""
Cryptographically Secure Pseudorandom Number Generator (CSPRNG).
Uses Python os.urandom / secrets for generating salts, nonces, and keys.

IEEE Mapping: Section IV-C (Entropy Subsystem)
"""

import secrets


def generate_salt(length: int = 16) -> bytes:
    """Generates a cryptographically secure random Salt byte sequence.

    Args:
        length: Desired salt length in bytes (default 16 bytes = 128 bits).

    Returns:
        Random salt bytes.

    Raises:
        ValueError: If length <= 0.
    """
    if length <= 0:
        raise ValueError("Salt length must be positive.")
    return secrets.token_bytes(length)


def generate_nonce(length: int = 12) -> bytes:
    """Generates a cryptographically secure random Nonce byte sequence.

    Args:
        length: Desired nonce length in bytes (default 12 bytes = 96 bits).

    Returns:
        Random nonce bytes.

    Raises:
        ValueError: If length <= 0.
    """
    if length <= 0:
        raise ValueError("Nonce length must be positive.")
    return secrets.token_bytes(length)
