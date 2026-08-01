"""
Encrypted Payload Dataclass & Serializer.

IEEE Mapping: Section IV-E (Payload Representation)
"""

from dataclasses import dataclass
import json
from crypto.models.exceptions import CorruptedPayloadError


@dataclass(frozen=True)
class EncryptedPackage:
    """Represents a serialized KDR-CA-AEAD encrypted payload package."""
    version: str
    salt: bytes
    nonce: bytes
    ciphertext: bytes
    tag: bytes

    def to_dict(self) -> dict[str, str]:
        """Serializes package to a JSON-compatible dictionary with hex values."""
        return {
            "version": self.version,
            "salt": self.salt.hex(),
            "nonce": self.nonce.hex(),
            "ciphertext": self.ciphertext.hex(),
            "tag": self.tag.hex(),
        }

    def to_json(self) -> str:
        """Serializes package to a JSON string."""
        return json.dumps(self.to_dict())

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> "EncryptedPackage":
        """Deserializes a dictionary into an EncryptedPackage object.

        Raises:
            CorruptedPayloadError: If required keys are missing or hex decoding fails.
        """
        required_keys = {"version", "salt", "nonce", "ciphertext", "tag"}
        if not required_keys.issubset(data.keys()):
            missing = required_keys - set(data.keys())
            raise CorruptedPayloadError(f"Missing payload fields: {missing}")

        try:
            return cls(
                version=data["version"],
                salt=bytes.fromhex(data["salt"]),
                nonce=bytes.fromhex(data["nonce"]),
                ciphertext=bytes.fromhex(data["ciphertext"]),
                tag=bytes.fromhex(data["tag"]),
            )
        except ValueError as err:
            raise CorruptedPayloadError(f"Hex decoding failed: {err}") from err

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
