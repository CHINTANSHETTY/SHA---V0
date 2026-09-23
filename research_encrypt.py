"""
Module: research_encrypt.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Standalone encryption module for Candidate C 10-round research cryptosystem.

Pipeline:
  Plaintext -> UTF-8 Binary -> 32-bit Length Header -> Zero Padding -> 256-bit Blocks
    -> Candidate C 10-Round Margolus CA Transform (ca_transform) -> XOR with SHA-512 K256 -> Ciphertext
"""

from research_crypto_utils import (
    derive_k256,
    text_to_binary,
    add_length_header,
    pad_to_256,
    split_into_blocks,
    xor_binary_strings,
    BLOCK_SIZE,
)
from ca_transform import transform_block_forward


def encrypt_research(plaintext: str, password: str) -> str:
    """
    Encrypts plaintext text string using SHA-512 K256 key + Candidate C 10-Round 2x2 Margolus CA + XOR.

    Args:
        plaintext: Input string payload to encrypt.
        password: User password string.

    Returns:
        Deterministic 256-bit binary string ciphertext.

    Raises:
        ValueError: If plaintext is not a string or password is empty.
    """
    if not isinstance(plaintext, str):
        raise ValueError(f"Plaintext must be a string, got {type(plaintext).__name__}.")

    if not password or not isinstance(password, str):
        raise ValueError("Password cannot be empty.")

    # Step 1: SHA-512 K256 key derivation (first 256 bits of SHA-512 hash)
    k256 = derive_k256(password)

    # Step 2: Plaintext UTF-8 -> Binary representation
    raw_binary = text_to_binary(plaintext)

    # Step 3: Add 32-bit binary length header
    framed_binary = add_length_header(raw_binary)

    # Step 4: Zero-pad to 256-bit block boundary
    padded_binary = pad_to_256(framed_binary)

    # Step 5: Split binary data into 256-bit blocks
    blocks = split_into_blocks(padded_binary, BLOCK_SIZE)

    # Step 6: Apply 2-Round Margolus CA transform + XOR with K256 for each block
    ciphertext_blocks = []
    for block in blocks:
        ca_transformed = transform_block_forward(block)
        cipher_block = xor_binary_strings(ca_transformed, k256)
        ciphertext_blocks.append(cipher_block)

    return "".join(ciphertext_blocks)


def run_demo() -> None:
    """Runs demonstration of research_encrypt module."""
    print("=" * 80)
    print(" REVISED RESEARCH ENCRYPTION MODULE DEMONSTRATION")
    print("=" * 80)

    sample_plaintext = "PatientID=P001;Age=45;Gender=F;BP=120/80;Diagnosis=Diabetes"
    sample_password = "HospitalDoctorKey2026#"

    print(f"\n1. Plaintext Input:  {sample_plaintext}")
    print(f"   Password:         {sample_password}")

    ciphertext = encrypt_research(sample_plaintext, sample_password)

    print(f"\n2. Ciphertext Output:")
    print(f"   Length:           {len(ciphertext)} bits (Divisible by 256: {len(ciphertext) % 256 == 0})")
    print(f"   First 64 bits:    {ciphertext[:64]}...")
    print(f"   Last 64 bits:     ...{ciphertext[-64:]}")
    print("=" * 80)


if __name__ == "__main__":
    run_demo()
