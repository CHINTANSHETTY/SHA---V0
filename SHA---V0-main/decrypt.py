from utils import (
    splitIntoBlocks,
    blocksToBinary,
    binaryToText
)

from shaModule import generateHash

from encrypt import (
    applyFbca,
    applyMorgolus,
    xorWithKey
)


# =========================================================
# REVERSE RIGHT SHIFT
# =========================================================

def reverseShift(blocks):

    if not blocks:
        return []

    return blocks[1:] + [blocks[0]]


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

    # SHA-512 password hash
    hashValue = generateHash(password)

    # Reverse XOR
    afterXor = xorWithKey(
        cipherText,
        hashValue
    )

    # Binary -> blocks
    blocks = splitIntoBlocks(afterXor)

    # Margolus is self-inverse
    reversedMorgolus = applyMorgolus(
        blocks
    )

    # Reverse circular shift
    reversedShift = reverseShift(
        reversedMorgolus
    )

    # FBCA is self-inverse
    reversedFbca = applyFbca(
        reversedShift
    )

    # Blocks -> original binary
    originalBinary = blocksToBinary(
        reversedFbca
    )

    # Binary -> original text
    originalText = binaryToText(
        originalBinary
    )

    return originalText