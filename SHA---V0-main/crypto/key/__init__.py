"""
Key Expansion Package for KDR-CA-AEAD.
"""

from crypto.key.derivation import (
    derive_blocks,
    derive_bytes,
    split_round_keys,
    validate_key_size,
)
from crypto.key.exceptions import (
    InvalidKeyError,
    InvalidKeySizeError,
    KeyDerivationError,
    KeyExpansionError,
)
from crypto.key.expansion import KeyExpansion

__all__ = [
    "KeyExpansion",
    "derive_bytes",
    "derive_blocks",
    "split_round_keys",
    "validate_key_size",
    "KeyExpansionError",
    "InvalidKeyError",
    "InvalidKeySizeError",
    "KeyDerivationError",
]
