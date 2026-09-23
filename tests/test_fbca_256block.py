import unittest
from encrypt import applyFbca, encryptRecord, applyMorgolus, createBinaryKey

from decrypt import decryptRecord
from shaModule import generateHash
from utils import textToBinary, padTo256, splitIntoBlocks


class TestFBCAEncryption(unittest.TestCase):

    def test_fbca_unit_rule(self):
        """
        Direct test for FBCA rule:
        00 -> 00
        01 -> 10
        10 -> 01
        11 -> 11
        And self-inverse behavior: FBCA(FBCA(x)) == x
        """
        # FBCA single 2-bit unit evaluation
        self.assertEqual(applyFbca("00"), "00", "FBCA('00') failed")
        self.assertEqual(applyFbca("01"), "10", "FBCA('01') failed")
        self.assertEqual(applyFbca("10"), "01", "FBCA('10') failed")
        self.assertEqual(applyFbca("11"), "11", "FBCA('11') failed")

        # Self-inverse verification
        self.assertEqual(applyFbca(applyFbca("00")), "00", "FBCA(FBCA('00')) failed")
        self.assertEqual(applyFbca(applyFbca("01")), "01", "FBCA(FBCA('01')) failed")
        self.assertEqual(applyFbca(applyFbca("10")), "10", "FBCA(FBCA('10')) failed")
        self.assertEqual(applyFbca(applyFbca("11")), "11", "FBCA(FBCA('11')) failed")

        # List of 2-bit units verification
        units = ["00", "01", "10", "11"]
        transformed = applyFbca(units)
        self.assertEqual(transformed, ["00", "10", "01", "11"])
        self.assertEqual(applyFbca(transformed), units)

    def test_sha512_k256_key_repetition(self):
        """
        Verify that createBinaryKey extracts the first 256 bits of SHA-512 (K256)
        and repeats K256 identically for every 256-bit block.
        """
        hashValue = generateHash("TestPassword123")
        fullHashBinary = "".join(format(int(c, 16), "04b") for c in hashValue)
        expectedK256 = fullHashBinary[:256]

        # Generate key for 3 blocks (768 bits)
        key768 = createBinaryKey(hashValue, 768)
        self.assertEqual(len(key768), 768)

        block1Key = key768[0:256]
        block2Key = key768[256:512]
        block3Key = key768[512:768]

        # Block 1, Block 2, Block 3 MUST use the SAME K256 key
        self.assertEqual(block1Key, expectedK256, "Block 1 does not match K256")
        self.assertEqual(block2Key, expectedK256, "Block 2 does not use the same K256 as Block 1")
        self.assertEqual(block3Key, expectedK256, "Block 3 does not use the same K256 as Block 1")

    def test_256bit_block_structure(self):
        """
        Verify that every encryption block is exactly 256 bits:
        256-bit input -> 1 x 256-bit block
        512-bit input -> 2 x 256-bit blocks
        768-bit input -> 3 x 256-bit blocks
        Non-multiple inputs pad only the final block.
        """
        # 256-bit input (32 chars)
        text_256 = "A" * 32
        bin_256 = textToBinary(text_256)
        self.assertEqual(len(bin_256), 256)
        padded_256 = padTo256(bin_256)
        blocks_256 = splitIntoBlocks(padded_256, 256)
        self.assertEqual(len(blocks_256), 1)
        self.assertEqual(len(blocks_256[0]), 256)

        # 512-bit input (64 chars)
        text_512 = "B" * 64
        bin_512 = textToBinary(text_512)
        self.assertEqual(len(bin_512), 512)
        padded_512 = padTo256(bin_512)
        blocks_512 = splitIntoBlocks(padded_512, 256)
        self.assertEqual(len(blocks_512), 2)
        self.assertTrue(all(len(b) == 256 for b in blocks_512))

        # 768-bit input (96 chars)
        text_768 = "C" * 96
        bin_768 = textToBinary(text_768)
        self.assertEqual(len(bin_768), 768)
        padded_768 = padTo256(bin_768)
        blocks_768 = splitIntoBlocks(padded_768, 256)
        self.assertEqual(len(blocks_768), 3)
        self.assertTrue(all(len(b) == 256 for b in blocks_768))

    def test_all_required_encryption_decryption_cases(self):
        """
        Verify 100% recovery for all required test cases:
        - Plaintext < 256 bits
        - Plaintext = 256 bits
        - Plaintext > 256 bits
        - Plaintext = 512 bits
        - Multiple 256-bit blocks
        - Plaintext ending in trailing zero bits
        - P101, Rahul, 28, A fever
        """
        test_cases = [
            ("P101, Rahul, 28, A fever", "SecretPass123!"),                     # TEST 1
            ("Hi", "Password123"),                                             # TEST 2: Short text (< 256 bits)
            ("12345678901234567890123456789012", "PassExact256"),               # TEST 3: Exactly 256 bits (32 bytes)
            ("Patient Short Data", "KeyShort"),                                 # TEST 4: Shorter than 256 bits
            ("This is a long patient record string containing extensive text beyond 256 bits.", "KeyLong"), # TEST 5: Longer than 256 bits
            ("1234567890123456789012345678901212345678901234567890123456789012", "PassExact512"), # TEST 6: Exactly 512 bits (64 bytes)
            ("P102, Anita, 45, Hypertension | Diagnosis: Stage 2 | Rx: Amlodipine 5mg", "DoctorKey2026#"), # TEST 7: Multi-block & custom key
            ("Healthcare Record ID #998811 - Confidential Patient Data", "AdminPass99!"), # Additional key/text test
            ("Patient string ending with trailing zero bits: @", "ZeroBitKey1"),  # ASCII '@' = 01000000 (ends in 6 zeros)
            ("Another text ending with P", "ZeroBitKey2"),                         # ASCII 'P' = 01010000 (ends in 4 zeros)
        ]

        for idx, (plaintext, password) in enumerate(test_cases, 1):
            encrypted = encryptRecord(plaintext, password)
            decrypted = decryptRecord(encrypted, password)
            self.assertEqual(
                decrypted,
                plaintext,
                f"Test Case {idx} failed: decrypted '{decrypted}' != plaintext '{plaintext}'"
            )

        print("100% Recovery Verified Across All Test Cases!")


if __name__ == "__main__":
    unittest.main()

