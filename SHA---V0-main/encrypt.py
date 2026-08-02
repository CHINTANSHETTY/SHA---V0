from utils import (
    textToBinary,
    splitIntoBlocks,
    blocksToBinary
)

from shaModule import generateHash


# =========================================================
# FBCA TRANSFORMATION
# =========================================================

def applyFbca(blocks):

    transformedBlocks = []

    for block in blocks:

        if len(block) != 8:
            raise ValueError("Invalid FBCA block.")

        bitSum = int(block[0]) + int(block[1])

        if bitSum % 2 == 1:

            flippedBlock = ""

            for bit in block:

                if bit == "0":
                    flippedBlock += "1"
                else:
                    flippedBlock += "0"

            transformedBlocks.append(flippedBlock)

        else:

            transformedBlocks.append(block)

    return transformedBlocks


# =========================================================
# RIGHT SHIFT
# =========================================================

def rightShift(blocks):

    if not blocks:
        return []

    return [blocks[-1]] + blocks[:-1]


# =========================================================
# MARGOLUS TRANSFORMATION
# =========================================================

def applyMorgolus(blocks):

    transformedBlocks = blocks.copy()

    for i in range(0, len(transformedBlocks) - 1, 2):

        transformedBlocks[i], transformedBlocks[i + 1] = (
            transformedBlocks[i + 1],
            transformedBlocks[i]
        )

    return transformedBlocks


# =========================================================
# CREATE REPEATING SHA KEY
# =========================================================

def createBinaryKey(hashValue, dataLength):

    binaryKey = ""

    for char in hashValue:
        binaryKey += format(int(char, 16), "04b")

    if not binaryKey:
        raise ValueError("Unable to generate encryption key.")

    repeatCount = (dataLength // len(binaryKey)) + 1

    repeatedKey = binaryKey * repeatCount

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

    # Text -> Binary
    binaryData = textToBinary(patientData)

    # Binary -> 8-bit blocks
    blocks = splitIntoBlocks(binaryData)

    # FBCA
    fbcaBlocks = applyFbca(blocks)

    # Right circular shift
    shiftedBlocks = rightShift(fbcaBlocks)

    # Margolus block transformation
    morgolusBlocks = applyMorgolus(shiftedBlocks)

    # Blocks -> Binary
    transformedBinary = blocksToBinary(
        morgolusBlocks
    )

    # SHA-512 password hash
    hashValue = generateHash(password)

    # XOR
    cipherText = xorWithKey(
        transformedBinary,
        hashValue
    )

    return cipherText