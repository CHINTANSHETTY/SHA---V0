"""
Module: research_decrypt.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Standalone decryption module for Candidate C 10-round research cryptosystem.

Pipeline:
  Ciphertext -> 256-bit Blocks -> Reverse XOR with SHA-512 K256
    -> Candidate C 10-Round Margolus CA Inverse Transform (ca_transform) -> 256-bit Plaintext Blocks
    -> Extract via 32-bit Length Header & Strip Padding -> UTF-8 Plaintext
"""

from research_crypto_utils import (
    derive_k256,
    binary_to_text,
    extract_with_length_header,
    split_into_blocks,
    xor_binary_strings,
    BLOCK_SIZE,
)
from ca_transform import transform_block_inverse
from research_encrypt import encrypt_research


def decrypt_research(ciphertext: str, password: str) -> str:
    """
    Decrypts ciphertext string using SHA-512 K256 key + Candidate C 10-Round 2x2 Margolus CA Inverse + Reverse XOR.

    Args:
        ciphertext: Binary string ciphertext ('0' and '1') divisible by 256.
        password: User password string.

    Returns:
        Original plaintext text string.

    Raises:
        ValueError: If inputs are invalid or ciphertext structure is corrupted.
    """
    if not isinstance(ciphertext, str) or not ciphertext:
        raise ValueError("Ciphertext cannot be empty.")

    if len(ciphertext) % BLOCK_SIZE != 0:
        raise ValueError(
            f"Invalid ciphertext length {len(ciphertext)}. Ciphertext must be divisible by 256 bits."
        )

    for idx, char in enumerate(ciphertext):
        if char not in ("0", "1"):
            raise ValueError(
                f"Invalid character '{char}' at index {idx} in ciphertext. Must contain only '0' or '1'."
            )

    if not password or not isinstance(password, str):
        raise ValueError("Password cannot be empty.")

    # Step 1: SHA-512 K256 key derivation
    k256 = derive_k256(password)

    # Step 2: Split ciphertext into 256-bit blocks
    ciphertext_blocks = split_into_blocks(ciphertext, BLOCK_SIZE)

    # Step 3: Reverse XOR with K256 + Apply 2-Round Margolus CA Inverse for each block
    restored_blocks = []
    for cipher_block in ciphertext_blocks:
        ca_transformed = xor_binary_strings(cipher_block, k256)
        orig_block = transform_block_inverse(ca_transformed)
        restored_blocks.append(orig_block)

    # Step 4: Concatenate blocks into full binary string
    padded_binary = "".join(restored_blocks)

    # Step 5: Extract original binary payload using 32-bit length header & discard padding
    raw_binary = extract_with_length_header(padded_binary)

    # Step 6: Binary -> UTF-8 text string
    return binary_to_text(raw_binary)


def run_demo() -> None:
    """Runs demonstration of research_decrypt module and full round-trip."""
    print("=" * 80)
    print(" REVISED RESEARCH DECRYPTION MODULE DEMONSTRATION")
    print("=" * 80)

    sample_plaintext = "PatientID=P001;Age=45;Gender=F;BP=120/80;Diagnosis=Diabetes"
    sample_password = "HospitalDoctorKey2026#"

    print(f"\n1. Original Plaintext: {sample_plaintext}")
    ciphertext = encrypt_research(sample_plaintext, sample_password)
    print(f"2. Encrypted Cipher:   {ciphertext[:64]}...")

    recovered_text = decrypt_research(ciphertext, sample_password)
    print(f"3. Decrypted Text:     {recovered_text}")

    match = (sample_plaintext == recovered_text)
    print(f"4. Round-Trip Match:   {match}")

    if match:
        print("\n   SUCCESS: decrypt_research(encrypt_research(P, K), K) == P is 100% verified!")
    else:
        print("\n   FAILURE: Plaintext mismatch in decryption round-trip.")

    print("=" * 80)


if __name__ == "__main__":
    run_demo()
