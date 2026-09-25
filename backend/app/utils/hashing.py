import hashlib

def calculate_sha256(content: bytes) -> str:
    """
    Calculate the SHA-256 hash from exact raw binary bytes.
    DO NOT modify bytes before hashing.
    """
    hasher = hashlib.sha256()
    hasher.update(content)
    return hasher.hexdigest()
