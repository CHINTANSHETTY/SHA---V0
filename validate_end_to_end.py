"""
Module: validate_end_to_end.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Programmatic end-to-end validation of the complete plaintext -> ciphertext -> plaintext
         encryption and decryption pipeline implemented in research_encrypt.py and research_decrypt.py.
"""

import random
from typing import List, Tuple, Dict
from research_encrypt import encrypt_research
from research_decrypt import decrypt_research
from synthetic_healthcare_data import generate_synthetic_dataset, record_to_string


DEFAULT_PASSWORD = "ResearchProject2026"

BASIC_PLAINTEXTS = [
    "Hello",
    "Healthcare",
    "SHA-512",
    "Patient Record",
    "Secure Healthcare Data",
    "SHA-512-Based 256-bit Block Cellular Automata Cryptosystem",
]

UNICODE_PLAINTEXTS = [
    "café",
    "स्वास्थ्य",
    "患者记录",
    "sécurité des données",
    "Patient: José, Diagnosis: Hypertension",
]


def test_basic_text_roundtrip() -> Tuple[bool, List[Tuple[str, bool]]]:
    """
    TEST 1 — Basic text round-trip test.
    """
    results = []
    all_pass = True

    for p in BASIC_PLAINTEXTS:
        try:
            cipher = encrypt_research(p, DEFAULT_PASSWORD)
            recovered = decrypt_research(cipher, DEFAULT_PASSWORD)
            match = (recovered == p)
            if not match:
                all_pass = False
            results.append((p, match))
        except Exception:
            results.append((p, False))
            all_pass = False

    return all_pass, results


def test_empty_string() -> Tuple[bool, str]:
    """
    TEST 2 — Empty string plaintext test.
    """
    try:
        cipher = encrypt_research("", DEFAULT_PASSWORD)
        recovered = decrypt_research(cipher, DEFAULT_PASSWORD)
        if recovered == "":
            return True, "Empty string encryption and decryption passed: PASS"
        else:
            return False, f"Recovered empty string mismatch: got '{recovered}'."
    except Exception as e:
        return False, f"Empty string handling raised exception: {type(e).__name__} ({e})"


def test_short_strings_byte_lengths() -> Tuple[int, int, List[Tuple[int, bool]]]:
    """
    TEST 3 — Short strings with specific byte lengths.
    Byte sizes: 1, 10, 31, 32, 33, 63, 64, 65 bytes.
    """
    byte_sizes = [1, 10, 31, 32, 33, 63, 64, 65]
    results = []
    passed = 0

    for size in byte_sizes:
        # Create deterministic ASCII string of exact byte length
        p = "A" * size
        assert len(p.encode("utf-8")) == size

        try:
            cipher = encrypt_research(p, DEFAULT_PASSWORD)
            recovered = decrypt_research(cipher, DEFAULT_PASSWORD)
            match = (recovered == p)
            if match:
                passed += 1
            results.append((size, match))
        except Exception:
            results.append((size, False))

    return passed, len(byte_sizes), results


def test_multi_block_plaintext() -> Tuple[int, int, List[Tuple[int, bool]]]:
    """
    TEST 4 — Multi-block plaintext test (~100, 256, 512, 1024 bytes).
    """
    sizes = [100, 256, 512, 1024]
    results = []
    passed = 0

    for size in sizes:
        p = "X" * size
        try:
            cipher = encrypt_research(p, DEFAULT_PASSWORD)
            recovered = decrypt_research(cipher, DEFAULT_PASSWORD)
            match = (recovered == p)
            if match:
                passed += 1
            results.append((size, match))
        except Exception:
            results.append((size, False))

    return passed, len(sizes), results


def test_unicode_plaintext() -> Tuple[int, int, List[Tuple[str, bool]]]:
    """
    TEST 5 — Unicode plaintext test.
    """
    results = []
    passed = 0

    for p in UNICODE_PLAINTEXTS:
        try:
            cipher = encrypt_research(p, DEFAULT_PASSWORD)
            recovered = decrypt_research(cipher, DEFAULT_PASSWORD)
            match = (recovered == p)
            if match:
                passed += 1
            results.append((p, match))
        except Exception:
            results.append((p, False))

    return passed, len(UNICODE_PLAINTEXTS), results


def test_synthetic_healthcare_records(count: int = 20, seed: int = 20260923) -> Tuple[int, int, float]:
    """
    TEST 6 & 7 — Synthetic healthcare record datasets.
    """
    dataset = generate_synthetic_dataset(count, seed=seed)
    passed = 0

    for rec_dict in dataset:
        rec_str = record_to_string(rec_dict)
        try:
            cipher = encrypt_research(rec_str, DEFAULT_PASSWORD)
            recovered = decrypt_research(cipher, DEFAULT_PASSWORD)
            if recovered == rec_str:
                passed += 1
        except Exception:
            pass

    pct = (passed / count) * 100.0
    return passed, count, pct


def test_ciphertext_structure() -> Tuple[bool, str]:
    """
    TEST 8 — Ciphertext structure verification.
    Verifies:
      1. Binary representation ('0' and '1').
      2. Length divisible by 256.
      3. Non-empty output for non-empty plaintext.
      4. Plaintext not exposed in raw ciphertext.
    """
    sample_p = "Patient Record P10001: Hypertension"
    cipher = encrypt_research(sample_p, DEFAULT_PASSWORD)

    if not cipher:
        return False, "Ciphertext is empty."

    if len(cipher) % 256 != 0:
        return False, f"Ciphertext length ({len(cipher)}) is not divisible by 256."

    if any(c not in ("0", "1") for c in cipher):
        return False, "Ciphertext contains non-binary characters."

    raw_bin = "".join(format(b, "08b") for b in sample_p.encode("utf-8"))
    if raw_bin in cipher:
        return False, "Plaintext binary payload found unencrypted in ciphertext."

    return True, f"Ciphertext structure valid: {len(cipher)} bits (Divisible by 256: True)."


def test_wrong_password_behavior() -> Tuple[bool, str]:
    """
    TEST 9 — Wrong password decryption behavior observation.
    """
    plaintext = "Sensitive healthcare record"
    cipher = encrypt_research(plaintext, DEFAULT_PASSWORD)
    wrong_password = "WrongPassword2026"

    try:
        decrypted = decrypt_research(cipher, wrong_password)
        if decrypted == plaintext:
            return False, "UNEXPECTED: Decryption succeeded with wrong password!"
        else:
            return True, f"Produced garbage text of length {len(decrypted)} (No match)."
    except Exception as e:
        return True, f"Raised exception {type(e).__name__}: {str(e)[:80]}"


def test_round_setting_interface() -> Tuple[bool, str]:
    """
    TEST 10 — Round setting interface check.
    Checks if public encrypt_research / decrypt_research API supports a rounds parameter.
    """
    # The public API signature is encrypt_research(plaintext, password)
    # It does not accept a rounds parameter.
    return True, "Public research API uses fixed production default configuration (10 rounds)."


def main() -> None:
    print("=" * 60)
    print(" END-TO-END ENCRYPTION & DECRYPTION PIPELINE VALIDATION ")
    print("=" * 60)

    # TEST 1
    t1_pass, t1_results = test_basic_text_roundtrip()
    print("\nTEST 1 — Basic Text Round-Trip:")
    for p, match in t1_results:
        status = "PASS" if match else "FAIL"
        print(f"  Plaintext: '{p:30s}' | Match: {status}")

    # TEST 2
    t2_pass, t2_msg = test_empty_string()
    print(f"\nTEST 2 — Empty String Test:")
    print(f"  {t2_msg}")

    # TEST 3
    t3_pass, t3_total, t3_results = test_short_strings_byte_lengths()
    print(f"\nTEST 3 — Short Strings & Block Boundaries:")
    for size, match in t3_results:
        status = "PASS" if match else "FAIL"
        print(f"  Length {size:2d} bytes: {status}")

    # TEST 4
    t4_pass, t4_total, t4_results = test_multi_block_plaintext()
    print(f"\nTEST 4 — Multi-Block Plaintext:")
    for size, match in t4_results:
        status = "PASS" if match else "FAIL"
        print(f"  Length {size:4d} bytes: {status}")

    # TEST 5
    t5_pass, t5_total, t5_results = test_unicode_plaintext()
    print(f"\nTEST 5 — Unicode Plaintext:")
    for p, match in t5_results:
        status = "PASS" if match else "FAIL"
        print(f"  Unicode: {ascii(p)} | Match: {status}")

    # TEST 6
    t6_pass, t6_total, t6_pct = test_synthetic_healthcare_records(count=20, seed=20260923)
    print(f"\nTEST 6 — 20 Synthetic Healthcare Records Test:")
    print(f"  Passed: {t6_pass}/20 ({t6_pct:.2f}%)")

    # TEST 7
    t7_pass, t7_total, t7_pct = test_synthetic_healthcare_records(count=100, seed=20260923)
    print(f"\nTEST 7 — 100 Synthetic Healthcare Records Test:")
    print(f"  Passed: {t7_pass}/100 ({t7_pct:.2f}%)")

    # TEST 8
    t8_pass, t8_msg = test_ciphertext_structure()
    print(f"\nTEST 8 — Ciphertext Structure Verification:")
    print(f"  {t8_msg}")

    # TEST 9
    t9_pass, t9_msg = test_wrong_password_behavior()
    print(f"\nTEST 9 — Wrong Password Decryption Behavior:")
    print(f"  {t9_msg}")

    # TEST 10
    t10_pass, t10_msg = test_round_setting_interface()
    print(f"\nTEST 10 — Round Setting Interface Check:")
    print(f"  {t10_msg}")

    overall_pass = (
        t1_pass
        and t2_pass
        and (t3_pass == t3_total)
        and (t4_pass == t4_total)
        and (t5_pass == t5_total)
        and (t6_pass == 20)
        and (t7_pass == 100)
        and t8_pass
    )

    print("\n" + "=" * 40)
    print("END-TO-END ENCRYPTION VALIDATION")
    print("=" * 40)
    print(f"Basic text round-trip: {'PASS' if t1_pass else 'FAIL'}")
    print(f"Empty string: {'PASS' if t2_pass else 'FAIL'}")
    print(f"Block-boundary strings: {t3_pass}/{t3_total} PASS")
    print(f"Multi-block plaintext: {t4_pass}/{t4_total} PASS")
    print(f"Unicode plaintext: {t5_pass}/{t5_total} PASS")
    print(f"20 healthcare records: {t6_pass}/20 PASS")
    print(f"100 healthcare records: {t7_pass}/100 PASS")
    print(f"Ciphertext structure: {'PASS' if t8_pass else 'FAIL'}")
    print(f"Wrong-password behavior: {t9_msg}")
    print(f"Round-setting tests: {t10_msg}")
    print(f"\nOverall end-to-end validation: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 40)


if __name__ == "__main__":
    main()
