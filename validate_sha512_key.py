"""
Module: validate_sha512_key.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Programmatic and cryptographic validation of SHA-512 to 256-bit key derivation (K256)
         and XOR compatibility in research_crypto_utils.py.
"""

import hashlib
import random
from typing import List, Tuple, Dict
from research_crypto_utils import derive_k256, xor_binary_strings, BLOCK_SIZE


TEST_PASSWORDS = [
    "test",
    "SHA512",
    "healthcare",
    "password123",
    "ResearchProject2026",
]

UNICODE_PASSWORDS = [
    "café",
    "स्वास्थ्य",
    "患者",
    "sécurité",
]


def test_sha512_digest_length() -> Tuple[bool, str]:
    """
    TEST 1 — SHA-512 digest length verification.
    Verifies full SHA-512 digest is 64 bytes (512 bits).
    """
    for pwd in TEST_PASSWORDS:
        digest = hashlib.sha512(pwd.encode("utf-8")).digest()
        if len(digest) != 64 or len(digest) * 8 != 512:
            return False, f"SHA-512 digest byte length for '{pwd}' is {len(digest)} (expected 64)."

    return True, "All test passwords produced exact 64-byte (512-bit) SHA-512 digests."


def test_k256_length() -> Tuple[bool, str]:
    """
    TEST 2 — K256 binary key length verification.
    Verifies derived key K256 is exactly 256 bits (characters).
    """
    for pwd in TEST_PASSWORDS:
        k256 = derive_k256(pwd)
        if len(k256) != 256 or not all(c in ("0", "1") for c in k256):
            return False, f"K256 length for '{pwd}' is {len(k256)} bits (expected 256 binary chars)."

    return True, "All derived K256 keys are exactly 256 binary characters."


def test_independent_hashlib_crosscheck() -> Tuple[bool, List[Tuple[str, str, str, bool]]]:
    """
    TEST 3 — Independent SHA-512 cross-check.
    Compares derive_k256(pwd) output against independent hashlib.sha512 byte extraction.
    """
    table = []
    all_match = True

    for pwd in TEST_PASSWORDS:
        # Independent calculation
        raw_digest = hashlib.sha512(pwd.encode("utf-8")).digest()
        first_32_bytes = raw_digest[:32]
        independent_k256 = "".join(format(b, "08b") for b in first_32_bytes)

        # Project derive_k256 calculation
        project_k256 = derive_k256(pwd)

        match = (independent_k256 == project_k256)
        if not match:
            all_match = False

        table.append((pwd, independent_k256, project_k256, match))

    return all_match, table


def test_different_passwords_uniqueness() -> Tuple[int, int, float, bool]:
    """
    TEST 4 — Different passwords produce unique K256 values.
    Empirical uniqueness check across 10 deterministic test passwords.
    """
    passwords = [f"password_sample_{i}_2026" for i in range(10)]
    k256_list = [derive_k256(p) for p in passwords]

    unique_keys = set(k256_list)
    num_passwords = len(passwords)
    num_unique = len(unique_keys)
    uniqueness_pct = (num_unique / num_passwords) * 100.0

    all_unique = (num_unique == num_passwords)
    return num_passwords, num_unique, uniqueness_pct, all_unique


def test_same_password_reproducibility() -> Tuple[bool, str]:
    """
    TEST 5 — Same password reproducibility test.
    Verifies derive_k256(pwd) is strictly deterministic.
    """
    for pwd in TEST_PASSWORDS:
        k256_1 = derive_k256(pwd)
        k256_2 = derive_k256(pwd)
        if k256_1 != k256_2:
            return False, f"Determinism failure for password '{pwd}'."

    return True, "Same password reproducibility verified: PASS"


def test_utf8_password_handling() -> Tuple[bool, List[Tuple[str, bool]]]:
    """
    TEST 6 — UTF-8 password handling test.
    Verifies handling of non-ASCII Unicode passwords and cross-checks with hashlib.
    """
    results = []
    all_pass = True

    for pwd in UNICODE_PASSWORDS:
        try:
            k256 = derive_k256(pwd)

            # Independent check
            raw_digest = hashlib.sha512(pwd.encode("utf-8")).digest()
            independent_k256 = "".join(format(b, "08b") for b in raw_digest[:32])

            match = (len(k256) == 256 and k256 == independent_k256)
            if not match:
                all_pass = False
            results.append((pwd, match))
        except Exception:
            results.append((pwd, False))
            all_pass = False

    return all_pass, results


def test_256bit_xor_compatibility(count: int = 100, seed: int = 42) -> Tuple[bool, int, int]:
    """
    TEST 7 — 256-bit XOR compatibility test.
    Verifies XOR operations between K256 and 256-bit blocks.
    """
    rng = random.Random(seed)
    pwd = "ResearchProject2026"
    k256 = derive_k256(pwd)

    if len(k256) != BLOCK_SIZE:
        return False, 0, count

    passed = 0
    failed = 0

    for _ in range(count):
        block = "".join(str(rng.randint(0, 1)) for _ in range(BLOCK_SIZE))
        cipher_block = xor_binary_strings(block, k256)

        if len(cipher_block) != BLOCK_SIZE:
            failed += 1
            continue

        recovered_block = xor_binary_strings(cipher_block, k256)
        if recovered_block == block:
            passed += 1
        else:
            failed += 1

    return (failed == 0), passed, failed


def main() -> None:
    print("=" * 60)
    print(" SHA-512 TO 256-BIT KEY DERIVATION (K256) VALIDATION ")
    print("=" * 60)

    # TEST 1
    t1_pass, t1_msg = test_sha512_digest_length()
    print(f"\nTEST 1 — SHA-512 Digest Length Check:")
    print(f"  {t1_msg}")

    # TEST 2
    t2_pass, t2_msg = test_k256_length()
    print(f"\nTEST 2 — K256 Key Length Check:")
    print(f"  {t2_msg}")

    # TEST 3
    t3_pass, table = test_independent_hashlib_crosscheck()
    print(f"\nTEST 3 — Independent hashlib.sha512 Cross-Check:")
    for pwd, ind_k, prj_k, match in table:
        status = "PASS" if match else "FAIL"
        print(f"  Password: '{pwd:20s}' | Independent K256 prefix: {ind_k[:16]}... | Match: {status}")

    # TEST 4
    num_p, num_u, uniq_pct, t4_pass = test_different_passwords_uniqueness()
    print(f"\nTEST 4 — Different Passwords Uniqueness Check:")
    print(f"  Number of passwords tested: {num_p}")
    print(f"  Number of unique K256 keys: {num_u}")
    print(f"  Uniqueness percentage:      {uniq_pct:.2f}%")

    # TEST 5
    t5_pass, t5_msg = test_same_password_reproducibility()
    print(f"\nTEST 5 — Same Password Reproducibility:")
    print(f"  {t5_msg}")

    # TEST 6
    t6_pass, unicode_results = test_utf8_password_handling()
    print(f"\nTEST 6 — UTF-8 Password Handling:")
    for pwd, match in unicode_results:
        status = "PASS" if match else "FAIL"
        print(f"  Unicode Password: {ascii(pwd)} | Match: {status}")

    # TEST 7
    t7_pass, xor_p, xor_f = test_256bit_xor_compatibility(count=100, seed=42)
    print(f"\nTEST 7 — 256-Bit XOR Compatibility & Reversibility (100 runs):")
    print(f"  Passed: {xor_p}/100 | Failed: {xor_f}/100")

    overall_pass = t1_pass and t2_pass and t3_pass and t4_pass and t5_pass and t6_pass and t7_pass

    print("\n" + "=" * 40)
    print("SHA-512 -> K256 VALIDATION")
    print("=" * 40)
    print(f"SHA-512 digest length: {'PASS' if t1_pass else 'FAIL'}")
    print(f"K256 length: {'PASS' if t2_pass else 'FAIL'}")
    print(f"Independent hashlib cross-check: {'PASS' if t3_pass else 'FAIL'}")
    print(f"Different-password uniqueness test: {'PASS' if t4_pass else 'FAIL'}")
    print(f"Same-password reproducibility: {'PASS' if t5_pass else 'FAIL'}")
    print(f"UTF-8 password test: {'PASS' if t6_pass else 'FAIL'}")
    print(f"256-bit XOR compatibility: {'PASS' if t7_pass else 'FAIL'}")
    print(f"\nOverall SHA-512/K256 validation: {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 40)

    if not overall_pass:
        print("\nFAILURE DETAILS:")
        if not t1_pass:
            print(f"TEST 1 Failure: {t1_msg}")
        if not t2_pass:
            print(f"TEST 2 Failure: {t2_msg}")
        if not t3_pass:
            for pwd, ind_k, prj_k, match in table:
                if not match:
                    print(f"TEST 3 Failure for '{pwd}': expected {ind_k}, got {prj_k}")
        if not t4_pass:
            print(f"TEST 4 Failure: Duplicate K256 key detected ({num_u}/{num_p} unique)")
        if not t5_pass:
            print(f"TEST 5 Failure: {t5_msg}")
        if not t6_pass:
            for pwd, match in unicode_results:
                if not match:
                    print(f"TEST 6 Failure for Unicode password {ascii(pwd)}")
        if not t7_pass:
            print(f"TEST 7 Failure: {xor_f} XOR block tests failed.")


if __name__ == "__main__":
    main()
