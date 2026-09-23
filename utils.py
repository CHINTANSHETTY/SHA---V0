def textToBinary(text):
    return "".join(format(ord(char), "08b") for char in text)


def binaryToText(binaryData):
    if len(binaryData) % 8 != 0:
        raise ValueError("Invalid binary data length.")

    text = ""
    for i in range(0, len(binaryData), 8):
        byte = binaryData[i:i + 8]
        text += chr(int(byte, 2))

    return text


def padTo256(binaryData):
    """
    Appends '0' bits to binary data to reach the next 256-bit boundary.
    If length is already a multiple of 256 bits, returns as is.
    """
    remainder = len(binaryData) % 256
    if remainder == 0:
        return binaryData

    padBits = 256 - remainder
    return binaryData + ("0" * padBits)


def addLengthHeader(binaryData):
    """
    Prepends a 32-bit binary header encoding the exact length of binaryData in bits.
    """
    header = format(len(binaryData), "032b")
    return header + binaryData


def extractWithLengthHeader(binaryData):
    """
    Extracts the 32-bit length header and returns the exact original binaryData.
    """
    if len(binaryData) < 32:
        raise ValueError("Binary data too short for length header.")

    origLen = int(binaryData[:32], 2)
    return binaryData[32:32 + origLen]



def splitIntoBlocks(binaryData, blockSize=256):
    """
    Splits binary data into blocks of blockSize bits (default 256).
    """
    if not binaryData:
        return []

    if len(binaryData) % blockSize != 0:
        raise ValueError(f"Binary data must be divisible into {blockSize}-bit blocks.")

    blocks = []
    for i in range(0, len(binaryData), blockSize):
        blocks.append(binaryData[i:i + blockSize])

    return blocks


def blocksToBinary(blocks):
    return "".join(blocks)