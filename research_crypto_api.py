"""
Module: research_crypto_api.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Application-facing API wrapper for the revised research cryptosystem.
         Connects the Flask application to research_encrypt and research_decrypt
         with optional text-safe Base64 encoding for database storage and UI display.
"""

import base64
from research_encrypt import encrypt_research
from research_decrypt import decrypt_research
from research_crypto_utils import BLOCK_SIZE

# Identifier prefix for revised research cipher packages
REVISED_PREFIX: str = "REV-CA-V1:"


def binary_to_base64(binary_str: str) -> str:
    """
    Converts a binary character string ('0' and '1') into a Base64 encoded string.
    The length of binary_str must be a multiple of 8 bits.
    """
    if len(binary_str) % 8 != 0:
        raise ValueError("Binary string length must be a multiple of 8 bits for Base64 conversion.")

    byte_vals = bytearray()
    for i in range(0, len(binary_str), 8):
        byte_vals.append(int(binary_str[i:i + 8], 2))

    b64_encoded = base64.b64encode(bytes(byte_vals)).decode("ascii")
    return REVISED_PREFIX + b64_encoded


def base64_to_binary(b64_payload: str) -> str:
    """
    Converts a Base64 encoded string back into a binary character string ('0' and '1').
    Strips 'REV-CA-V1:' prefix if present.
    """
    if b64_payload.startswith(REVISED_PREFIX):
        b64_str = b64_payload[len(REVISED_PREFIX):]
    else:
        b64_str = b64_payload

    raw_bytes = base64.b64decode(b64_str.encode("ascii"))
    return "".join(format(b, "08b") for b in raw_bytes)


def encrypt_payload(patient_data: str, password: str) -> str:
    """
    Encrypts a patient record string using the revised research cryptosystem.

    Pipeline:
      1. research_encrypt.encrypt_research(patient_data, password) -> 256-bit binary ciphertext
      2. Converts binary ciphertext to Base64 string prefixed with 'REV-CA-V1:'

    Args:
        patient_data: Patient record string (e.g., 'P001|Name|Age|...').
        password: User decryption password string.

    Returns:
        Base64-encoded ciphertext string for application storage and display.
    """
    binary_ciphertext = encrypt_research(patient_data, password)
    return binary_to_base64(binary_ciphertext)


def decrypt_payload(ciphertext_payload: str, password: str) -> str:
    """
    Decrypts a patient record ciphertext string using the revised research cryptosystem.

    Accepts:
      - Base64 string prefixed with 'REV-CA-V1:'
      - Raw Base64 string
      - Raw binary string ('0' and '1') divisible by 256 bits

    Args:
        ciphertext_payload: Ciphertext string.
        password: User password string.

    Returns:
        Original patient record string.
    """
    if not ciphertext_payload:
        raise ValueError("Ciphertext payload cannot be empty.")

    if ciphertext_payload.startswith(REVISED_PREFIX) or not all(c in "01" for c in ciphertext_payload):
        binary_ciphertext = base64_to_binary(ciphertext_payload)
    else:
        binary_ciphertext = ciphertext_payload

    return decrypt_research(binary_ciphertext, password)


def run_demo() -> None:
    """Runs demonstration of research_crypto_api module."""
    print("=" * 80)
    print(" APPLICATION RESEARCH CRYPTO API DEMONSTRATION")
    print("=" * 80)

    sample_patient = "P101|Rahul|28|Male|Fever|Viral Fever|Paracetamol 500mg"
    sample_password = "DoctorPassword123!"

    print(f"\n1. Original Patient Record: {sample_patient}")
    print(f"   Encryption Password:     {sample_password}")

    # Application-level Encryption
    b64_ciphertext = encrypt_payload(sample_patient, sample_password)
    print(f"\n2. Application Ciphertext (Base64):")
    print(f"   Payload:                 {b64_ciphertext}")

    # Extract raw binary ciphertext length for verification
    raw_binary = base64_to_binary(b64_ciphertext)
    print(f"   Underlying Binary Bits:  {len(raw_binary)} bits (Divisible by 256: {len(raw_binary) % BLOCK_SIZE == 0})")

    # Application-level Decryption
    recovered_patient = decrypt_payload(b64_ciphertext, sample_password)
    print(f"\n3. Decrypted Patient Record: {recovered_patient}")

    match = (sample_patient == recovered_patient)
    print(f"4. Exact Match Verification: {match}")

    if match:
        print("\n   SUCCESS: Active application research crypto API verified 100%!")
    else:
        print("\n   FAILURE: Plaintext mismatch in application API decryption.")

    print("=" * 80)


if __name__ == "__main__":
    run_demo()
