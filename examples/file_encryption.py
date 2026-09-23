#!/usr/bin/env python3
"""
File Encryption Example - KDR-CA-AEAD v1.0.0

This script demonstrates secure file payload encryption and decryption
with header metadata authentication.
"""

import os
from crypto import encrypt_bytes, decrypt_bytes


def main():
    print("=" * 60)
    print("  KDR-CA-AEAD v1.0.0 - File Payload Encryption Demo")
    print("=" * 60)

    master_key = b"Nagamrutha_Research_Master_Key_32B"
    sample_file = "sample_data.txt"
    file_content = b"Telemetry Record: Voltage=12.4V, Temp=24.5C, Timestamp=2026-08-05T20:45:00Z"

    # Create dummy sample file
    with open(sample_file, "wb") as f:
        f.write(file_content)
    print(f"\n[1] Created sample file '{sample_file}' ({len(file_content)} bytes).")

    # Read and encrypt file content
    with open(sample_file, "rb") as f:
        data = f.read()

    header_metadata = f"Filename:{sample_file};Size:{len(data)}".encode('utf-8')
    pkg = encrypt_bytes(data, master_key, associated_data=header_metadata)
    print("\n[2] File content encrypted with metadata authentication header.")

    # Decrypt file content
    decrypted_data = decrypt_bytes(pkg, master_key, associated_data=header_metadata)
    assert decrypted_data == file_content, "Decrypted data mismatch!"
    print(f"[3] Decryption successful! Recovered {len(decrypted_data)} bytes.")

    # Clean up dummy file
    if os.path.exists(sample_file):
        os.remove(sample_file)
    print("\n[SUCCESS] File encryption demonstration completed!")


if __name__ == "__main__":
    main()
