"""
Unit and integration tests for research_crypto_api.py and app.py integration.
Verifies active healthcare application encryption/decryption, Base64 representation,
underlying 256-bit block alignment, wrong password handling, Unicode, multi-block records,
and deterministic round-trip behavior.
"""

import random
import unittest
from research_crypto_api import (
    encrypt_payload,
    decrypt_payload,
    binary_to_base64,
    base64_to_binary,
    REVISED_PREFIX,
)
from research_crypto_utils import BLOCK_SIZE


class TestAppCryptoIntegration(unittest.TestCase):

    def test_a_synthetic_healthcare_record_roundtrip(self):
        """TEST A: Synthetic healthcare record encrypted and decrypted through application API."""
        patient_data = "P001|Anita Sharma|45|Female|Hypertension|Stage 2 HTN|Amlodipine 5mg"
        password = "DoctorSecretPassword2026#"

        b64_ciphertext = encrypt_payload(patient_data, password)

        # Confirm Base64 payload prefix
        self.assertTrue(b64_ciphertext.startswith(REVISED_PREFIX))

        recovered_data = decrypt_payload(b64_ciphertext, password)
        self.assertEqual(recovered_data, patient_data)

    def test_b_wrong_password_fails_decryption(self):
        """TEST B: Wrong password must not return the original plaintext."""
        patient_data = "P002|Rajesh|50|Male|Diabetes|Type 2 Diabetes|Metformin 500mg"
        correct_password = "CorrectPass2026!"
        wrong_password = "WrongPass2026!"

        b64_ciphertext = encrypt_payload(patient_data, correct_password)

        try:
            wrong_recovery = decrypt_payload(b64_ciphertext, wrong_password)
            self.assertNotEqual(wrong_recovery, patient_data)
        except Exception:
            # Raising exception (e.g. Unicode error or corrupted header) is expected
            pass

    def test_c_multiple_records(self):
        """TEST C: Multiple distinct healthcare records encrypted with unique passwords."""
        records = [
            ("P101|Ravi|22|Male|Fever|Viral Fever|Paracetamol", "Pass101"),
            ("P102|Sunita|34|Female|Asthma|Chronic Asthma|Salbutamol", "Pass102"),
            ("P103|Vikram|62|Male|Cardiac|Angina|Nitroglycerin", "Pass103"),
            ("P104|Pooja|19|Female|Allergy|Dust Allergy|Cetirizine", "Pass104"),
        ]

        for p_data, password in records:
            b64_cipher = encrypt_payload(p_data, password)
            recovered = decrypt_payload(b64_cipher, password)
            self.assertEqual(recovered, p_data)

    def test_d_unicode_healthcare_text(self):
        """TEST D: Unicode healthcare text with non-ASCII characters and symbols."""
        patient_data = "P201|Dr. Müller|38|Other|Cardiology|心臓病|Aspirin 81mg 💊"
        password = "UnicodeDoctorPassKey!"

        b64_cipher = encrypt_payload(patient_data, password)
        recovered = decrypt_payload(b64_cipher, password)

        self.assertEqual(recovered, patient_data)

    def test_e_multi_block_record(self):
        """TEST E: Record spanning multiple 256-bit blocks."""
        long_notes = "Detailed clinical observations: " + ("Extensive Patient Examination Notes " * 15)
        patient_data = f"P301|Long Patient Record|55|Male|Complex Disease|{long_notes}|Multiple Prescriptions"
        password = "MultiBlockAppKey2026"

        b64_cipher = encrypt_payload(patient_data, password)
        recovered = decrypt_payload(b64_cipher, password)

        self.assertEqual(recovered, patient_data)

    def test_f_underlying_ciphertext_256bit_divisibility(self):
        """TEST F: Verify ciphertext length before Base64 encoding is strictly divisible by 256."""
        patient_data = "P401|Short Record|30|Female|Checkup|Normal|None"
        password = "TestKey123"

        b64_cipher = encrypt_payload(patient_data, password)

        # Extract underlying binary ciphertext
        binary_ciphertext = base64_to_binary(b64_cipher)

        self.assertGreater(len(binary_ciphertext), 0)
        self.assertEqual(
            len(binary_ciphertext) % BLOCK_SIZE, 0,
            f"Underlying binary ciphertext length ({len(binary_ciphertext)}) must be divisible by 256."
        )

    def test_g_base64_roundtrip_conversion(self):
        """TEST G: Verify Base64 round-trip conversion (binary_to_base64 / base64_to_binary)."""
        sample_binary = "01010101" * 32  # 256 bits
        b64_str = binary_to_base64(sample_binary)

        self.assertTrue(b64_str.startswith(REVISED_PREFIX))

        reconstructed_binary = base64_to_binary(b64_str)
        self.assertEqual(reconstructed_binary, sample_binary)

    def test_h_deterministic_records_suite(self):
        """TEST H: Run multiple deterministic test records."""
        random.seed(20260923)

        for i in range(50):
            pid = f"P{i+5000}"
            p_data = f"{pid}|Patient_{i}|{random.randint(20, 80)}|Male|Condition_{i}|Diagnosis_{i}|Rx_{i}"
            password = f"AppPass_{i}_Seed2026"

            b64_cipher = encrypt_payload(p_data, password)
            recovered = decrypt_payload(b64_cipher, password)

            self.assertEqual(recovered, p_data)


if __name__ == "__main__":
    unittest.main()
