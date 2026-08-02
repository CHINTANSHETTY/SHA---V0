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


def splitIntoBlocks(binaryData):

    if not binaryData:
        return []

    if len(binaryData) % 8 != 0:
        raise ValueError("Binary data must be divisible into 8-bit blocks.")

    blocks = []

    for i in range(0, len(binaryData), 8):
        blocks.append(binaryData[i:i + 8])

    return blocks


def blocksToBinary(blocks):
    return "".join(blocks)