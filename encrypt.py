from utils import (
    textToBinary,
    addLengthHeader,
    padTo256,
    splitIntoBlocks,
    blocksToBinary
)

from shaModule import generateHash


# =========================================================
# FBCA TRANSFORMATION (2-bit local units)
# =========================================================

def applyFbca(units):
    """
    Applies Flip-Bit Cellular Automaton (FBCA) to 2-bit local unit(s).
    00 -> 00
    01 -> 10
    10 -> 01
    11 -> 11
    If bit sum is odd, flip both bits. If even, keep unchanged.
    Self-inverse: FBCA(FBCA(N)) == N.
    """
    if isinstance(units, str):
        if len(units) != 2:
            raise ValueError("Invalid FBCA 2-bit unit length.")
        bitSum = int(units[0]) + int(units[1])
        if bitSum % 2 == 1:
            return ("0" if units[0] == "1" else "1") + ("0" if units[1] == "1" else "1")
        return units

    if isinstance(units, list):
        return [applyFbca(u) for u in units]

    raise ValueError("Invalid FBCA input type.")


# =========================================================
# RIGHT SHIFT (1-position circular right shift of 2-bit units)
# =========================================================

def rightShift(units):
    """
    Performs a 1-position circular right shift on a list of 2-bit units.
    Before: [N1, N2, N3, ..., N128]
    After:  [N128, N1, N2, ..., N127]
    """
    if not units:
        return []
    return [units[-1]] + units[:-1]


# =========================================================
# MARGOLUS TRANSFORMATION (Round 1 FBCA -> 2-bit Right Shift -> Round 2 FBCA)
# =========================================================

def applyMorgolus(block):
    """
    Applies the Margolus/FBCA transformation to 256-bit block(s).
    For each 256-bit block:
      1. Split into 128 x 2-bit units.
      2. Apply FBCA Round 1.
      3. Right shift 2-bit units by 1 position.
      4. Apply FBCA Round 2.
    """
    if isinstance(block, list):
        return [applyMorgolus(b) for b in block]

    if len(block) != 256:
        raise ValueError(f"Margolus block must be exactly 256 bits, got {len(block)} bits.")

    # 1. Divide 256-bit block into 128 x 2-bit units
    units = [block[i:i + 2] for i in range(0, 256, 2)]

    # 2. Round 1: FBCA
    fbca1Units = applyFbca(units)

    # 3. 1-position circular right shift of 2-bit units
    shiftedUnits = rightShift(fbca1Units)

    # 4. Round 2: FBCA
    fbca2Units = applyFbca(shiftedUnits)

    # Reassemble into 256-bit transformed block
    return "".join(fbca2Units)


# =========================================================
# CREATE REPEATING SHA-512 K256 KEY
# =========================================================

def createBinaryKey(hashValue, dataLength):
    """
    Generates encryption key material from SHA-512 hash:
    1. Converts 128 hex chars to 512-bit binary hash.
    2. Extracts first 256 bits as K256.
    3. Repeats K256 identically for every 256-bit block.
    """
    binaryKey = ""
    for char in hashValue:
        binaryKey += format(int(char, 16), "04b")

    if not binaryKey:
        raise ValueError("Unable to generate encryption key.")

    # Extract exact first 256 bits as K256
    key256 = binaryKey[:256]

    # Repeat K256 for every 256-bit block
    repeatCount = (dataLength + 255) // 256
    repeatedKey = key256 * repeatCount

    return repeatedKey[:dataLength]


# =========================================================
# XOR
# =========================================================

def xorWithKey(binaryData, hashValue):

    binaryKey = createBinaryKey(
        hashValue,
        len(binaryData)
    )

    result = ""

    for dataBit, keyBit in zip(binaryData, binaryKey):

        if dataBit == keyBit:
            result += "0"
        else:
            result += "1"

    return result


# =========================================================
# ENCRYPT RECORD
# =========================================================

def encryptRecord(patientData, password):

    if not patientData:
        raise ValueError("Patient data cannot be empty.")

    if not password:
        raise ValueError("Password cannot be empty.")

    # 1. Text -> Binary
    binaryData = textToBinary(patientData)

    # 2. Add 32-bit length header
    framedBinary = addLengthHeader(binaryData)

    # 3. Zero-pad to 256-bit boundary
    paddedBinary = padTo256(framedBinary)

    # 4. Binary -> 256-bit blocks
    blocks = splitIntoBlocks(paddedBinary, 256)

    # 5. Apply Margolus / FBCA 256-bit transformations
    morgolusBlocks = applyMorgolus(blocks)

    # 6. Blocks -> Binary
    transformedBinary = blocksToBinary(morgolusBlocks)

    # 7. SHA-512 password hash
    hashValue = generateHash(password)

    # 8. AddKey / XOR with K256
    cipherText = xorWithKey(
        transformedBinary,
        hashValue
    )

    return cipherText
