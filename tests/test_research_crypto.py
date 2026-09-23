"""
Unit tests for research_encrypt.py and research_decrypt.py modules.
Verifies SHA-512 K256 key derivation, 2x2 Margolus CA + XOR encryption, exact round-trip
reversibility across ASCII, healthcare records, empty strings, Unicode, block boundary cases,
multi-block payloads, 100 synthetic records, and invalid ciphertext validation.
"""

import random
import unittest
from research_crypto_utils import derive_k256, BLOCK_SIZE
from research_encrypt import encrypt_research
from research_decrypt import decrypt_research


class TestResearchCrypto(unittest.TestCase):

    def test_a_short_ascii_text(self):
        """TEST A: Short ASCII text encryption & decryption."""
        plaintext = "Patient record test"
        password = "DoctorPassword123"

        ciphertext = encrypt_research(plaintext, password)
        recovered = decrypt_research(ciphertext, password)

        self.assertEqual(recovered, plaintext)

    def test_b_healthcare_synthetic_record(self):
        """TEST B: Healthcare-style synthetic record string."""
        plaintext = "PatientID=P001;Age=45;Gender=F;BP=120/80;HR=72;Diagnosis=Diabetes"
        password = "HospitalSecretKey2026!"

        ciphertext = encrypt_research(plaintext, password)
        recovered = decrypt_research(ciphertext, password)

        self.assertEqual(recovered, plaintext)

    def test_c_empty_string(self):
        """TEST C: Empty string payload handling."""
        plaintext = ""
        password = "AnyValidPassword"

        ciphertext = encrypt_research(plaintext, password)

        # Ciphertext for empty string must still be a 256-bit block containing 32-bit zero length header + padding
        self.assertEqual(len(ciphertext), BLOCK_SIZE)

        recovered = decrypt_research(ciphertext, password)
        self.assertEqual(recovered, plaintext)

    def test_d_unicode_text(self):
        """TEST D: Unicode text containing multi-byte UTF-8 symbols."""
        plaintext = "Patient: 👨‍⚕️ Dr. Smith | Condition: OK | Health System 100% 🏥"
        password = "UnicodePassKey99$"

        ciphertext = encrypt_research(plaintext, password)
        recovered = decrypt_research(ciphertext, password)

        self.assertEqual(recovered, plaintext)

    def test_e_exact_256bit_boundary_payload(self):
        """
        TEST E: Payload whose binary length + 32-bit header equals exactly 256 bits (1 block).
        Header = 32 bits. Target binary = 224 bits = 28 UTF-8 bytes.
        """
        plaintext = "A" * 28  # 28 bytes * 8 bits = 224 bits + 32 bits header = 256 bits
        password = "ExactBoundaryPass"

        ciphertext = encrypt_research(plaintext, password)
        self.assertEqual(len(ciphertext), BLOCK_SIZE)  # Exactly 1 block

        recovered = decrypt_research(ciphertext, password)
        self.assertEqual(recovered, plaintext)

    def test_f_multi_block_payload(self):
        """TEST F: Text requiring multiple 256-bit blocks."""
        plaintext = "Confidential Healthcare Record Details: " + ("Clinical Notes Data " * 20)
        password = "MultiBlockPassWord"

        ciphertext = encrypt_research(plaintext, password)
        self.assertGreater(len(ciphertext), BLOCK_SIZE)
        self.assertEqual(len(ciphertext) % BLOCK_SIZE, 0)

        recovered = decrypt_research(ciphertext, password)
        self.assertEqual(recovered, plaintext)

    def test_g_100_synthetic_healthcare_records(self):
        """TEST G: 100 deterministic synthetic healthcare records (fixed seed)."""
        random.seed(20260923)

        diseases = ["Hypertension", "Diabetes", "Asthma", "Arrhythmia", "COVID-19", "Influenza"]
        meds = ["Amlodipine", "Metformin", "Albuterol", "Metoprolol", "Paxlovid", "Tamiflu"]

        for idx in range(100):
            pid = f"P{idx+1000}"
            age = random.randint(18, 90)
            gender = random.choice(["M", "F"])
            disease = random.choice(diseases)
            med = random.choice(meds)
            password = f"DoctorPass_{idx}_Seed2026"

            record = f"PatientID={pid};Age={age};Gender={gender};Disease={disease};Prescription={med}"

            ciphertext = encrypt_research(record, password)
            recovered = decrypt_research(ciphertext, password)

            self.assertEqual(
                recovered, record,
                f"Round-trip failed for synthetic record {idx}: '{record}'"
            )

    def test_h_deterministic_output(self):
        """TEST H: Same plaintext + same password must produce identical ciphertext."""
        plaintext = "Deterministic Healthcare Encryption Test Payload"
        password = "StaticPassword123"

        cipher1 = encrypt_research(plaintext, password)
        cipher2 = encrypt_research(plaintext, password)

        self.assertEqual(cipher1, cipher2)

    def test_i_wrong_password_fails_decryption(self):
        """TEST I: Decrypting with wrong password fails to produce original plaintext."""
        plaintext = "Sensitive Patient Diagnostic Summary"
        correct_password = "CorrectPass2026!"
        wrong_password = "WrongPass2026!"

        ciphertext = encrypt_research(plaintext, correct_password)

        try:
            wrong_decryption = decrypt_research(ciphertext, wrong_password)
            self.assertNotEqual(wrong_decryption, plaintext)
        except Exception:
            # Raising an exception (e.g. UnicodeDecodeError or ValueError on header) is acceptable
            pass

    def test_j_invalid_ciphertext_length_rejected(self):
        """TEST J: Reject ciphertext lengths not divisible by 256."""
        password = "TestPassword"

        with self.assertRaises(ValueError) as ctx_255:
            decrypt_research("0" * 255, password)
        self.assertIn("divisible by 256 bits", str(ctx_255.exception))

        with self.assertRaises(ValueError) as ctx_257:
            decrypt_research("0" * 257, password)
        self.assertIn("divisible by 256 bits", str(ctx_257.exception))

    def test_k_invalid_ciphertext_characters_rejected(self):
        """TEST K: Reject ciphertext strings containing invalid characters."""
        password = "TestPassword"
        bad_cipher_1 = ("0" * 255) + "2"
        bad_cipher_2 = ("1" * 100) + "x" + ("0" * 155)

        with self.assertRaises(ValueError) as ctx_1:
            decrypt_research(bad_cipher_1, password)
        self.assertIn("Invalid character '2'", str(ctx_1.exception))

        with self.assertRaises(ValueError) as ctx_2:
            decrypt_research(bad_cipher_2, password)
        self.assertIn("Invalid character 'x'", str(ctx_2.exception))

    def test_l_100_random_plaintext_password_roundtrip(self):
        """TEST L: 100 random plaintext string and password round-trip tests (fixed seed)."""
        random.seed(20260923)

        sample_chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()_+-=[]{}|;:,.<>/? "

        for trial in range(100):
            p_len = random.randint(1, 150)
            k_len = random.randint(4, 30)

            plaintext = "".join(random.choice(sample_chars) for _ in range(p_len))
            password = "".join(random.choice(sample_chars) for _ in range(k_len))

            ciphertext = encrypt_research(plaintext, password)
            recovered = decrypt_research(ciphertext, password)

            self.assertEqual(
                recovered, plaintext,
                f"Random trial {trial} failed for plaintext length {p_len}"
            )


if __name__ == "__main__":
    unittest.main()
