import hashlib


def generateHash(password):
    """
    Generates a SHA-512 hash for the given password.
    Returns a 128-character hexadecimal string.
    """

    sha = hashlib.sha512()

    sha.update(password.encode("utf-8"))

    hashValue = sha.hexdigest()

    return hashValue