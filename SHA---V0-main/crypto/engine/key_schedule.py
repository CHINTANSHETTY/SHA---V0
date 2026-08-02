"""
Key Schedule & Dynamic Sub-Key Expansion Engine.

IEEE Mapping: Section IV-B (Key Schedule Subsystem)
"""

from crypto.primitives.hkdf import hkdf
from crypto.models.exceptions import KeyDerivationError


class KeySchedule:
    """Manages derivation and expansion of sub-keys (K_r, K_c, K_a) from master passwords."""

    def __init__(self, master_password: str, salt: bytes, nonce: bytes):
        """Initializes KeySchedule and expands 96-bit sub-key material.

        Args:
            master_password: Low-entropy master password string.
            salt: 16-byte random salt.
            nonce: 12-byte random nonce.

        Raises:
            KeyDerivationError: If parameters are missing or invalid.
        """
        if not master_password:
            raise KeyDerivationError("Master password cannot be empty.")

        if not salt or len(salt) != 16:
            raise KeyDerivationError("Salt must be exactly 16 bytes.")

        if not nonce or len(nonce) != 12:
            raise KeyDerivationError("Nonce must be exactly 12 bytes.")

        self.salt = salt
        self.nonce = nonce

        # Expand 96 bytes via HKDF-SHA256
        info = b"KDR-CA-AEAD-v1-subkeys|" + nonce
        ikm = master_password.encode("utf-8")
        
        okm = hkdf(ikm=ikm, length=96, salt=salt, info=info)

        self._ca_rule_key = okm[:32]      # K_r (32 bytes)
        self._cipher_key = okm[32:64]     # K_c (32 bytes)
        self._mac_key = okm[64:96]        # K_a (32 bytes)

    def get_ca_rule_table(self) -> list[int]:
        """Derives a list of 32 8-bit Cellular Automata local transition rule numbers.

        Returns:
            List of 32 integers in range [0, 255].
        """
        return list(self._ca_rule_key)

    def get_cipher_key(self) -> bytes:
        """Returns 32-byte encryption key K_c."""
        return self._cipher_key

    def get_mac_key(self) -> bytes:
        """Returns 32-byte HMAC authentication key K_a."""
        return self._mac_key
