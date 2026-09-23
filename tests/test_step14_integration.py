"""
Module: test_step14_integration.py
Project: SHA-512 Healthcare Encryption Project (Candidate C Integration)
Purpose: Comprehensive unit test suite for Step 14 production integration of Candidate C architecture.

Verifies:
  1. Active 10-round Candidate C architecture specification:
     - Standard Margolus partition on odd rounds
     - Shifted Margolus partition on even rounds
     - Circular matrix shift DOWN 2 / RIGHT 2 in forward direction
     - Inverse circular matrix shift UP 2 / LEFT 2 in reverse direction
     - SHA-512 key derivation -> first 256 bits = K256
     - 256-bit framing (32-bit length header, zero padding)
  2. Loss-less reversibility across blocks and payloads
  3. Healthcare data recovery (ASCII, Unicode, multi-block, 100 synthetic EHR records)
  4. Deterministic Known-Answer Test (KAT)
  5. Audit confirmation: zero forbidden cryptographic primitives (HKDF, HMAC, AES, nonce, salt)
"""

import unittest
import random
import sys
from typing import List

from ca_matrix import (
    block_to_matrix,
    matrix_to_block,
    validate_block,
    validate_matrix,
    BLOCK_SIZE,
    MATRIX_ROWS,
    MATRIX_COLS,
)
from margolus_ca import apply_margolus_forward, apply_margolus_inverse
from margolus_shifted import apply_shifted_margolus_forward, apply_shifted_margolus_inverse
from ca_transform import (
    circular_shift_matrix,
    inverse_circular_shift_matrix,
    transform_block_forward,
    transform_block_inverse,
    DEFAULT_ROUNDS,
)
from research_crypto_utils import (
    derive_k256,
    text_to_binary,
    binary_to_text,
    add_length_header,
    extract_with_length_header,
    pad_to_256,
    split_into_blocks,
    xor_binary_strings,
)
from research_encrypt import encrypt_research
from research_decrypt import decrypt_research
from research_crypto_api import (
    encrypt_payload,
    decrypt_payload,
    REVISED_PREFIX,
)
from synthetic_healthcare_data import (
    generate_synthetic_dataset,
    record_to_string,
)


class TestStep14Integration(unittest.TestCase):

    def test_01_candidate_C_architecture_specification(self):
        """Verify Candidate C default parameters and 10-round alternating partition pipeline."""
        self.assertEqual(DEFAULT_ROUNDS, 10)

        # Test forward circular shift DOWN 2, RIGHT 2 formula
        m = [[0] * 16 for _ in range(16)]
        m[0][0] = 1
        shifted = circular_shift_matrix(m, row_shift=2, col_shift=2)
        self.assertEqual(shifted[2][2], 1)
        self.assertEqual(shifted[0][0], 0)

        # Test inverse circular shift UP 2, LEFT 2 formula
        restored = inverse_circular_shift_matrix(shifted, row_shift=2, col_shift=2)
        self.assertEqual(restored[0][0], 1)
        self.assertEqual(restored[2][2], 0)

        # Test single block forward step-by-step match with 10-round loop
        block = "01" * 128
        matrix = block_to_matrix(block)
        for r in range(1, 11):
            if r % 2 != 0:
                matrix = apply_margolus_forward(matrix)
            else:
                matrix = apply_shifted_margolus_forward(matrix)
            matrix = circular_shift_matrix(matrix, row_shift=2, col_shift=2)
        expected_block = matrix_to_block(matrix)

        self.assertEqual(transform_block_forward(block), expected_block)

    def test_02_sha512_k256_derivation(self):
        """Verify SHA-512 derivation produces exactly 256-bit K256 string."""
        password = "HospitalDoctorKey2026#"
        k256 = derive_k256(password)

        self.assertEqual(len(k256), 256)
        self.assertTrue(all(c in "01" for c in k256))

        # Expected K256 for "HospitalDoctorKey2026#" in hex
        expected_hex = "0xc4e0babe07a5aa1870dcba322e9c74d1faf1295794662f87e82213baee7d489d"
        actual_hex = hex(int(k256, 2))
        self.assertEqual(actual_hex, expected_hex)

    def test_03_256bit_framing_and_length_header(self):
        """Verify 32-bit length header and 256-bit padding framing."""
        raw_text = "PatientID=P001"
        raw_bin = text_to_binary(raw_text)

        framed = add_length_header(raw_bin)
        self.assertEqual(len(framed), len(raw_bin) + 32)
        self.assertEqual(framed[:32], format(len(raw_bin), "032b"))

        padded = pad_to_256(framed)
        self.assertEqual(len(padded) % 256, 0)

        extracted = extract_with_length_header(padded)
        self.assertEqual(extracted, raw_bin)
        self.assertEqual(binary_to_text(extracted), raw_text)

    def test_04_exact_block_reversibility_100_trials(self):
        """Verify exact loss-less block reversibility across 100 random 256-bit blocks."""
        random.seed(20260923)
        for trial in range(100):
            bits = [str(random.randint(0, 1)) for _ in range(256)]
            blk = "".join(bits)

            transformed = transform_block_forward(blk)
            recovered = transform_block_inverse(transformed)

            self.assertEqual(
                recovered, blk,
                f"Block transformation round-trip failed on trial {trial}"
            )

    def test_05_healthcare_ordinary_ascii_roundtrip(self):
        """Verify encryption and decryption for ordinary ASCII healthcare records."""
        plaintext = "PatientID=P001;Age=45;Gender=F;BP=120/80;Diagnosis=Diabetes"
        password = "DoctorPassword123!"

        c_bin = encrypt_research(plaintext, password)
        p_dec = decrypt_research(c_bin, password)
        self.assertEqual(p_dec, plaintext)

        c_b64 = encrypt_payload(plaintext, password)
        self.assertTrue(c_b64.startswith(REVISED_PREFIX))
        p_b64_dec = decrypt_payload(c_b64, password)
        self.assertEqual(p_b64_dec, plaintext)

    def test_06_healthcare_unicode_roundtrip(self):
        """Verify encryption and decryption for Unicode healthcare data."""
        unicode_records = [
            "PatientID=P002;Doctor=Dr. Müller;Diagnosis=Cardiomyopathy;Note=Patient feel 75% better; Temp=36.6°C",
            "PatientID=P003;Name=José Gómez;Prescription=Vitamin C & D3;Status=Normal ✓",
            "PatientID=P004;Name=田中太郎;Hospital=東京総合病院;BloodType=AB+",
        ]
        password = "UnicodeSecureKey2026!"

        for rec in unicode_records:
            c_b64 = encrypt_payload(rec, password)
            rec_dec = decrypt_payload(c_b64, password)
            self.assertEqual(rec_dec, rec)

    def test_07_healthcare_multiblock_roundtrip(self):
        """Verify encryption and decryption for multi-block healthcare records (>500 chars)."""
        multi_block_record = "MultiBlockEHRHeader|" + ("A" * 600) + "|FooterNote"
        password = "MultiBlockKey2026#"

        c_bin = encrypt_research(multi_block_record, password)
        self.assertGreater(len(c_bin), 256)
        self.assertEqual(len(c_bin) % 256, 0)

        p_dec = decrypt_research(c_bin, password)
        self.assertEqual(p_dec, multi_block_record)

    def test_08_100_synthetic_healthcare_records_recovery(self):
        """Verify loss-less recovery for 100 synthetic healthcare records."""
        records = generate_synthetic_dataset(100, seed=20260923)
        password = "DoctorSyntheticPassphrase2026!"

        for idx, rec in enumerate(records):
            rec_str = record_to_string(rec)
            c_b64 = encrypt_payload(rec_str, password)
            rec_dec = decrypt_payload(c_b64, password)
            self.assertEqual(
                rec_dec, rec_str,
                f"Synthetic record decryption mismatch at index {idx}"
            )

    def test_09_deterministic_known_answer_test(self):
        """Deterministic Known-Answer Test (KAT) with fixed inputs and outputs."""
        fixed_plaintext = "PatientID=P001;Age=45;Gender=F;BP=120/80;Diagnosis=Diabetes"
        fixed_password = "HospitalDoctorKey2026#"

        expected_k256_hex = "0xc4e0babe07a5aa1870dcba322e9c74d1faf1295794662f87e82213baee7d489d"
        expected_cipher_b64 = "REV-CA-V1:Pmy4cytO0iASK/u/s1PKoEbAEQpyCOV9E9Cm8iR2cgNXz/SzXIJe8Jyw0+/OWCI2fNTKWFyqs6xk1fLAf4qsNA=="

        # 1. Verify K256 hex
        actual_k256 = derive_k256(fixed_password)
        self.assertEqual(hex(int(actual_k256, 2)), expected_k256_hex)

        # 2. Verify Ciphertext Base64 string
        actual_cipher_b64 = encrypt_payload(fixed_plaintext, fixed_password)
        self.assertEqual(actual_cipher_b64, expected_cipher_b64)

        # 3. Verify Decryption of expected Base64 string
        actual_decrypted = decrypt_payload(expected_cipher_b64, fixed_password)
        self.assertEqual(actual_decrypted, fixed_plaintext)

    def test_10_prohibited_crypto_primitives_audit(self):
        """Audit active research path to confirm no forbidden cryptographic primitives exist."""
        forbidden_terms = ["hkdf", "hmac", "aes", "nonce", "salt", "kdr_ca_aead"]

        target_modules = [
            "ca_transform",
            "research_encrypt",
            "research_decrypt",
            "research_crypto_api",
        ]

        for mod_name in target_modules:
            mod = sys.modules[mod_name]
            with open(mod.__file__, "r", encoding="utf-8") as f:
                content = f.read().lower()

            for term in forbidden_terms:
                self.assertNotIn(
                    term, content,
                    f"Forbidden primitive term '{term}' found in active module {mod_name}"
                )


if __name__ == "__main__":
    unittest.main()
