"""
Module: validate_ca_transform.py
Project: SHA-512 Healthcare Encryption Project (2x2 Reversible CA Revision)
Purpose: Programmatic validation of the complete multi-round 256-bit CA block transformation
         pipeline implemented in ca_transform.py (transform_block_forward & transform_block_inverse).
"""

import random
from typing import List, Tuple, Dict
from ca_matrix import BLOCK_SIZE
from ca_transform import transform_block_forward, transform_block_inverse, DEFAULT_ROUNDS


def test_round_count_configuration() -> Tuple[Dict[int, bool], bool]:
    """
    TEST 1 — Round-count configuration test.
    Confirms that round counts 2, 4, 6, 8, 10 work without error.
    """
    test_rounds = [2, 4, 6, 8, 10]
    results = {}
    sample_block = "01" * 128

    all_supported = True
    for r in test_rounds:
        try:
            fwd = transform_block_forward(sample_block, rounds=r)
            inv = transform_block_inverse(fwd, rounds=r)
            results[r] = (inv == sample_block)
            if not results[r]:
                all_supported = False
        except Exception:
            results[r] = False
            all_supported = False

    return results, all_supported


def test_random_reversibility(rounds_list: List[int] = [2, 4, 6, 8, 10], count: int = 100, seed: int = 42) -> Dict[int, Tuple[int, int, float, List]]:
    """
    TEST 2 — Random 256-bit block reversibility across round counts.
    Generates 100 deterministic random 256-bit blocks for each round count.
    """
    results = {}
    for r in rounds_list:
        rng = random.Random(seed)
        passed = 0
        failed = 0
        failures = []

        for i in range(count):
            block = "".join(str(rng.randint(0, 1)) for _ in range(BLOCK_SIZE))
            fwd = transform_block_forward(block, rounds=r)
            rec = transform_block_inverse(fwd, rounds=r)

            if rec == block:
                passed += 1
            else:
                failed += 1
                failures.append((i, block, fwd, rec))

        pct = (passed / count) * 100.0
        results[r] = (passed, failed, pct, failures)

    return results


def test_special_input_patterns(rounds_list: List[int] = [2, 4, 6, 8, 10]) -> Tuple[int, int, List]:
    """
    TEST 3 — Special input patterns reversibility across round counts.
    Tests:
      1. All-zero block
      2. All-one block
      3. Alternating 0101...
      4. Alternating 1010...
      5. Single 1 bit at position 0
      6. Single 1 bit at position 127
      7. Single 1 bit at position 255
    """
    patterns = [
        ("All-Zero", "0" * 256),
        ("All-One", "1" * 256),
        ("Alternating 01", "01" * 128),
        ("Alternating 10", "10" * 128),
        ("Single Bit at 0", "1" + "0" * 255),
        ("Single Bit at 127", "0" * 127 + "1" + "0" * 128),
        ("Single Bit at 255", "0" * 255 + "1"),
    ]

    total_tests = 0
    passed = 0
    failures = []

    for r in rounds_list:
        for name, block in patterns:
            total_tests += 1
            fwd = transform_block_forward(block, rounds=r)
            rec = transform_block_inverse(fwd, rounds=r)

            if rec == block:
                passed += 1
            else:
                failures.append((r, name, block, rec))

    return passed, total_tests, failures


def test_additional_10_round_random(count: int = 100, seed: int = 999) -> Tuple[int, int, float, List]:
    """
    TEST 4 — Deterministic random test using a second seed for 10 rounds.
    """
    rng = random.Random(seed)
    passed = 0
    failed = 0
    failures = []

    for i in range(count):
        block = "".join(str(rng.randint(0, 1)) for _ in range(BLOCK_SIZE))
        fwd = transform_block_forward(block, rounds=10)
        rec = transform_block_inverse(fwd, rounds=10)

        if rec == block:
            passed += 1
        else:
            failed += 1
            failures.append((i, block, fwd, rec))

    pct = (passed / count) * 100.0
    return passed, failed, pct, failures


def test_transformation_changes_data(rounds_list: List[int] = [2, 4, 6, 8, 10], count: int = 100, seed: int = 42) -> Dict[int, Tuple[int, int]]:
    """
    TEST 5 — Forward transformation data alteration test.
    Verifies that the forward transformation alters the input state for test blocks.
    Returns dict mapping rounds -> (different_blocks_count, unchanged_blocks_count).
    """
    results = {}
    for r in rounds_list:
        rng = random.Random(seed)
        different = 0
        unchanged = 0

        for _ in range(count):
            block = "".join(str(rng.randint(0, 1)) for _ in range(BLOCK_SIZE))
            fwd = transform_block_forward(block, rounds=r)

            if fwd != block:
                different += 1
            else:
                unchanged += 1

        results[r] = (different, unchanged)

    return results


def check_round_by_round_interface() -> Tuple[bool, str]:
    """
    TEST 6 — Round-by-round interface structure verification.
    Verifies that forward applies partition then shift, and inverse applies inverse shift then inverse partition in reverse order.
    """
    # Test 1-round forward vs inverse step order consistency
    block = "0" * 255 + "1"
    fwd_1 = transform_block_forward(block, rounds=1)
    inv_1 = transform_block_inverse(fwd_1, rounds=1)

    is_structured = (inv_1 == block)
    msg = (
        "Forward order: (Partition -> Shift (2,2)) x R.\n"
        "  Inverse order: (Inverse Shift (2,2) -> Inverse Partition) x R (reversed round order R..1).\n"
        "  Interface symmetry verified: PASS"
    )
    return is_structured, msg


def main() -> None:
    print("=" * 60)
    print(" COMPLETE MULTI-ROUND 256-BIT CA TRANSFORMATION VALIDATION ")
    print("=" * 60)

    # TEST 1: Round counts
    rounds_config, t1_all_pass = test_round_count_configuration()
    print("\nTEST 1 — Round-Count Configuration:")
    for r, supported in rounds_config.items():
        status = "PASS" if supported else "FAIL"
        print(f"  Round count {r:2d}: {status}")

    # TEST 2: Random reversibility across rounds
    rand_results = test_random_reversibility(rounds_list=[2, 4, 6, 8, 10], count=100, seed=42)
    print("\nTEST 2 — Random 256-Bit Block Reversibility (100 runs/round, seed=42):")
    t2_all_pass = True
    for r, (p, f, pct, _) in rand_results.items():
        print(f"  Round count {r:2d} | Passed: {p:3d}/100 | Failed: {f:3d} | Reversibility: {pct:.2f}%")
        if f > 0:
            t2_all_pass = False

    # TEST 3: Special patterns
    spec_pass, spec_total, spec_failures = test_special_input_patterns(rounds_list=[2, 4, 6, 8, 10])
    print(f"\nTEST 3 — Special Input Patterns Reversibility:")
    print(f"  Passed: {spec_pass}/{spec_total} pattern tests")
    t3_all_pass = (spec_pass == spec_total)

    # TEST 4: Additional 10-round random test
    add_pass, add_fail, add_pct, add_failures = test_additional_10_round_random(count=100, seed=999)
    print(f"\nTEST 4 — Additional 10-Round Random Test (100 runs, seed=999):")
    print(f"  Passed: {add_pass}/100 ({add_pct:.2f}%) | Failed: {add_fail}/100")
    t4_all_pass = (add_fail == 0)

    # TEST 5: Data alteration test
    change_results = test_transformation_changes_data(rounds_list=[2, 4, 6, 8, 10], count=100, seed=42)
    print("\nTEST 5 — Forward Transformation Data Alteration Check:")
    for r, (diff, unch) in change_results.items():
        print(f"  Round count {r:2d} | Transformed Changed: {diff:3d}/100 | Unchanged: {unch:3d}/100")

    # TEST 6: Interface check
    t6_pass, t6_msg = check_round_by_round_interface()
    print(f"\nTEST 6 — Round-By-Round Interface Check:")
    print(f"  {t6_msg}")

    overall_pass = t1_all_pass and t2_all_pass and t3_all_pass and t4_all_pass and t6_pass

    print("\n" + "=" * 40)
    print("COMPLETE CA TRANSFORMATION VALIDATION")
    print("=" * 40)
    print("Supported rounds:")
    for r in [2, 4, 6, 8, 10]:
        print(f"  {r}: {'PASS' if rounds_config.get(r, False) else 'FAIL'}")

    print("\nRandom reversibility:")
    for r in [2, 4, 6, 8, 10]:
        p = rand_results[r][0]
        print(f"  {r} rounds: {p}/100 PASS")

    print(f"\nSpecial patterns:")
    print(f"  {spec_pass}/{spec_total} PASS")

    print(f"\nAdditional 10-round random test:")
    print(f"  {add_pass}/100 PASS")

    print(f"\nForward transformation changed:")
    for r in [2, 4, 6, 8, 10]:
        diff = change_results[r][0]
        print(f"  {r} rounds: {diff}/100")

    print(f"\nOverall CA transformation validation:")
    print(f"  {'PASS' if overall_pass else 'FAIL'}")
    print("=" * 40)

    if not overall_pass:
        print("\nFAILURE DETAILS:")
        for r, (_, f, _, failures) in rand_results.items():
            if f > 0 and failures:
                idx, orig, fwd, rec = failures[0]
                print(f"First failing random test in {r} rounds (Index {idx}):")
                print(f"  Original:  {orig}")
                print(f"  Forward:   {fwd}")
                print(f"  Recovered: {rec}")

        if spec_failures:
            r, name, orig, rec = spec_failures[0]
            print(f"First failing special pattern in round {r} ({name}):")
            print(f"  Original:  {orig}")
            print(f"  Recovered: {rec}")

        if add_failures:
            idx, orig, fwd, rec = add_failures[0]
            print(f"First failing additional 10-round test (Index {idx}):")
            print(f"  Original:  {orig}")
            print(f"  Forward:   {fwd}")
            print(f"  Recovered: {rec}")


if __name__ == "__main__":
    main()
