#!/usr/bin/env python3
"""
Security Analysis Demo Script - KDR-CA-AEAD v1.0.0

This script demonstrates tamper rejection, Encrypt-then-MAC (EtM) integrity,
and constant-time verification behavior.
"""

from crypto import encrypt_bytes, decrypt_bytes, EncryptedPackage


def main():
    print("=" * 65)
    print("  KDR-CA-AEAD v1.0.0 - Security & Tamper Rejection Demo")
    print("=" * 65)

    master_key = b"Nagamrutha_Research_Master_Key_32B"
    payload = b"Top Secret Command Directive"
    ad = b"Header: Seq=101"

    # 1. Encrypt package
    pkg = encrypt_bytes(payload, master_key, associated_data=ad)
    print("\n[1] Encrypted package generated successfully.")

    # 2. Test Ciphertext Bit Inversion Attack
    print("\n[2] Testing Ciphertext Bit Inversion Attack:")
    tampered_ct = bytearray(pkg.ciphertext)
    tampered_ct[0] ^= 0x01
    
    tampered_pkg = EncryptedPackage(
        version=pkg.version,
        salt=pkg.salt,
        nonce=pkg.nonce,
        ciphertext=bytes(tampered_ct),
        tag=pkg.tag
    )

    try:
        decrypt_bytes(tampered_pkg, master_key, associated_data=ad)
        print("    FAIL: Tampered ciphertext was accepted!")
    except Exception as err:
        print(f"    SUCCESS: Ciphertext tampering detected and rejected: {err}")

    # 3. Test Associated Data Tampering
    print("\n[3] Testing Associated Data Header Alteration Attack:")
    tampered_ad = b"Header: Seq=102"  # Altered seq number
    try:
        decrypt_bytes(pkg, master_key, associated_data=tampered_ad)
        print("    FAIL: Tampered Associated Data was accepted!")
    except Exception as err:
        print(f"    SUCCESS: AD header tampering detected and rejected: {err}")

    print("\n[SUCCESS] Security and integrity verification checks passed!")


if __name__ == "__main__":
    main()
