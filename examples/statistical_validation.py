#!/usr/bin/env python3
"""
Statistical Validation Demo Script - KDR-CA-AEAD v1.0.0

This script demonstrates empirical Strict Avalanche Criterion (SAC) bit-flip
ratio sampling across random 1-bit plaintext perturbations.
"""

import random
from crypto import encrypt_bytes


def count_differing_bits(bytes1: bytes, bytes2: bytes) -> int:
    return sum(bin(b1 ^ b2).count('1') for b1, b2 in zip(bytes1, bytes2))


def main():
    print("=" * 65)
    print("  KDR-CA-AEAD v1.0.0 - Strict Avalanche Criterion (SAC) Demo")
    print("=" * 65)

    master_key = b"Nagamrutha_Research_Master_Key_32B"
    num_trials = 50
    total_bit_changes = 0
    total_bits = 0

    print(f"\nEvaluating Strict Avalanche Criterion over {num_trials} bit-flip trials...")

    for i in range(num_trials):
        # 16-byte random payload
        pt1 = bytearray(random.randbytes(16))
        pt2 = bytearray(pt1)

        # Flip 1 random bit in pt2
        byte_idx = random.randint(0, 15)
        bit_idx = random.randint(0, 7)
        pt2[byte_idx] ^= (1 << bit_idx)

        # Encrypt both under identical salt/nonce if re-used or random
        pkg1 = encrypt_bytes(bytes(pt1), master_key)
        pkg2 = encrypt_bytes(bytes(pt2), master_key)

        min_len = min(len(pkg1.ciphertext), len(pkg2.ciphertext))
        changed_bits = count_differing_bits(pkg1.ciphertext[:min_len], pkg2.ciphertext[:min_len])
        bit_capacity = min_len * 8

        total_bit_changes += changed_bits
        total_bits += bit_capacity

    empirical_sac = (total_bit_changes / total_bits) * 100
    print(f"\nEmpirical SAC Ratio (Sample Size {num_trials} trials): {empirical_sac:.2f}%")
    print("Theoretical Ideal SAC: 50.00%")
    print("\n[SUCCESS] Statistical avalanche sampling completed!")


if __name__ == "__main__":
    main()
