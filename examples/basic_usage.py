#!/usr/bin/env python3
"""
Basic Usage Example - KDR-CA-AEAD v1.0.0

This script demonstrates basic payload encryption, decryption, and verification
using the KDR-CA-AEAD reference implementation.
"""

from crypto import encrypt_bytes, decrypt_bytes


def main():
    print("=" * 60)
    print("  KDR-CA-AEAD v1.0.0 - Basic Usage Demonstration")
    print("=" * 60)

    # Define 32-byte (256-bit) Master Key
    master_key = b"Nagamrutha_Research_Master_Key_32B"
    plaintext = b"Confidential Medical Telemetry Payload - Patient ID 1004"
    associated_data = b"Header: Hospital-ID=H-44"

    print(f"\n[1] Original Plaintext : {plaintext.decode('utf-8')}")
    print(f"[2] Associated Data    : {associated_data.decode('utf-8')}")

    # Perform Encrypt-then-MAC AEAD Encryption
    pkg = encrypt_bytes(plaintext, master_key, associated_data=associated_data)

    print("\n[3] Encryption Successful!")
    print(f"    - Version         : {pkg.version}")
    print(f"    - Ciphertext (hex): {pkg.ciphertext.hex()[:40]}...")
    print(f"    - Salt (hex)      : {pkg.salt.hex()}")
    print(f"    - Nonce (hex)     : {pkg.nonce.hex()}")
    print(f"    - MAC Tag (hex)   : {pkg.tag.hex()[:40]}...")

    # Perform Decryption & Tag Verification
    recovered = decrypt_bytes(pkg, master_key, associated_data=associated_data)
    print(f"\n[4] Decrypted Output  : {recovered.decode('utf-8')}")

    assert recovered == plaintext, "Error: Decrypted payload does not match original!"
    print("\n[SUCCESS] Roundtrip encryption and tag verification verified!")


if __name__ == "__main__":
    main()
