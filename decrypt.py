from utils import (
    splitIntoBlocks,
    blocksToBinary,
    binaryToText,
    extractWithLengthHeader
)

from shaModule import generateHash

from encrypt import (
    applyFbca,
    xorWithKey
)


# =========================================================
# REVERSE CIRCULAR SHIFT (1-position circular left shift of 2-bit units)
# =========================================================

def reverseShift(units):
    """
    Performs a 1-position circular left shift on a list of 2-bit units.
    Before: [N128, N1, N2, ..., N127]
    After:  [N1, N2, N3, ..., N128]
    """
    if not units:
        return []
    return units[1:] + [units[0]]


# =========================================================
# REVERSE MARGOLUS TRANSFORMATION
# =========================================================

def reverseMorgolus(block):
    """
    Reverses the Margolus/FBCA transformation for 256-bit block(s).
    For each 256-bit block:
      1. Split into 128 x 2-bit units (FBCA Round 2 output).
      2. Reverse FBCA Round 2 (apply FBCA to each unit).
      3. Reverse circular shift (1-position left shift of 2-bit units).
      4. Reverse FBCA Round 1 (apply FBCA to each unit).
    """
    if isinstance(block, list):
        return [reverseMorgolus(b) for b in block]

    if len(block) != 256:
        raise ValueError(f"Margolus block must be exactly 256 bits, got {len(block)} bits.")

    # 1. Divide 256-bit block into 128 x 2-bit units
    fbca2Units = [block[i:i + 2] for i in range(0, 256, 2)]

    # 2. Reverse Round 2: FBCA
    shiftedUnits = applyFbca(fbca2Units)

    # 3. 1-position circular left shift of 2-bit units
    fbca1Units = reverseShift(shiftedUnits)

    # 4. Reverse Round 1: FBCA
    originalUnits = applyFbca(fbca1Units)

    # Reassemble into 256-bit block string
    return "".join(originalUnits)


# =========================================================
# DECRYPT RECORD
# =========================================================

def decryptRecord(cipherText, password):

    if not cipherText:
        raise ValueError("Cipher text cannot be empty.")

    if not password:
        raise ValueError("Password cannot be empty.")

    # Validate cipher text
    if any(bit not in "01" for bit in cipherText):
        raise ValueError("Cipher text contains invalid characters.")

    # 1. SHA-512 password hash
    hashValue = generateHash(password)

    # 2. Reverse XOR with K256
    afterXor = xorWithKey(
        cipherText,
        hashValue
    )

    # 3. Binary -> 256-bit blocks
    blocks = splitIntoBlocks(afterXor, 256)

    # 4. Reverse Margolus / FBCA 256-bit transformations
    reversedBlocks = reverseMorgolus(blocks)

    # 5. Blocks -> Binary
    paddedBinary = blocksToBinary(reversedBlocks)

    # 6. Extract original binary payload using length header
    originalBinary = extractWithLengthHeader(paddedBinary)

    # 7. Binary -> original text
    originalText = binaryToText(originalBinary)

    return originalText
