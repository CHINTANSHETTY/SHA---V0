"""
Encrypted Payload Dataclass & Serializer.

IEEE Mapping: Section IV-E (Payload Representation)
"""

from dataclasses import dataclass
import json
from crypto.models.exceptions import CorruptedPayloadError


def bytes_to_binary(data: bytes) -> str:
    """Converts bytes into a binary bitstream string (0s and 1s), 8 bits per byte."""
    return "".join(f"{b:08b}" for b in data)


def binary_to_bytes(binary_str: str) -> bytes:
    """Converts a binary bitstream string (0s and 1s) back into bytes.

    Raises:
        ValueError: If length is not a multiple of 8 or contains non-binary characters.
    """
    clean_str = "".join(binary_str.split())
    if len(clean_str) % 8 != 0:
        raise ValueError(f"Binary string length ({len(clean_str)}) must be a multiple of 8.")
    if any(c not in "01" for c in clean_str):
        raise ValueError("Binary string must contain only '0' and '1'.")
    return bytes(int(clean_str[i:i+8], 2) for i in range(0, len(clean_str), 8))


def hex_to_binary(hex_str: str) -> str:
    """Utility function to convert a hex string to a binary bitstream string."""
    return bytes_to_binary(bytes.fromhex(hex_str))


def binary_to_hex(binary_str: str) -> str:
    """Utility function to convert a binary bitstream string to a hex string."""
    return binary_to_bytes(binary_str).hex()


@dataclass(frozen=True)
class EncryptedPackage:
    """Represents a serialized KDR-CA-AEAD encrypted payload package."""
    version: str
    salt: bytes
    nonce: bytes
    ciphertext: bytes
    tag: bytes

    def to_dict(self) -> dict[str, str]:
        """Serializes package to a JSON-compatible dictionary with binary ciphertext and hex salt/nonce/tag."""
        return {
            "version": self.version,
            "salt": self.salt.hex(),
            "nonce": self.nonce.hex(),
            "ciphertext": bytes_to_binary(self.ciphertext),
            "tag": self.tag.hex(),
        }

    def to_json(self) -> str:
        """Serializes package to a JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "EncryptedPackage":
        """Deserializes a dictionary into an EncryptedPackage object.

        Supports both binary bitstream (0s and 1s) and legacy hex formatted ciphertext.

        Raises:
            CorruptedPayloadError: If required keys are missing or decoding fails.
        """
        required_keys = {"version", "salt", "nonce", "ciphertext", "tag"}
        if not required_keys.issubset(data.keys()):
            missing = required_keys - set(data.keys())
            raise CorruptedPayloadError(f"Missing payload fields: {missing}")

        try:
            salt_bytes = bytes.fromhex(data["salt"])
            nonce_bytes = bytes.fromhex(data["nonce"])
            tag_bytes = bytes.fromhex(data["tag"])
        except ValueError as err:
            raise CorruptedPayloadError(f"Hex decoding failed for salt/nonce/tag: {err}") from err

        raw_ct = data["ciphertext"]
        clean_ct = "".join(raw_ct.split())
        ciphertext_bytes = None

        # Format detection: If ciphertext contains only 0s and 1s, and length is a multiple of 8
        if clean_ct and all(c in "01" for c in clean_ct) and len(clean_ct) % 8 == 0:
            try:
                ciphertext_bytes = binary_to_bytes(clean_ct)
            except ValueError:
                ciphertext_bytes = None

        # Fallback for legacy hex ciphertext or non-binary strings
        if ciphertext_bytes is None:
            try:
                ciphertext_bytes = bytes.fromhex(raw_ct)
            except ValueError as err:
                raise CorruptedPayloadError(f"Ciphertext decoding failed (neither valid binary bitstream nor hex): {err}") from err

        return cls(
            version=data["version"],
            salt=salt_bytes,
            nonce=nonce_bytes,
            ciphertext=ciphertext_bytes,
            tag=tag_bytes,
        )

    @classmethod
    def from_json(cls, json_str: str) -> "EncryptedPackage":
        """Deserializes a JSON string into an EncryptedPackage object.

        Raises:
            CorruptedPayloadError: If JSON formatting or payload fields are invalid.
        """
        try:
            data = json.loads(json_str)
            if not isinstance(data, dict):
                raise CorruptedPayloadError("JSON payload must be an object.")
            return cls.from_dict(data)
        except json.JSONDecodeError as err:
            raise CorruptedPayloadError(f"Invalid JSON string: {err}") from err
