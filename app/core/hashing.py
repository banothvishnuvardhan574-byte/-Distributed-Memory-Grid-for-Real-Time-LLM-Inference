import hashlib


def hash_prompt(prompt: str) -> str:
    """Return a stable SHA-256 hash of a whitespace-trimmed prompt."""
    return hashlib.sha256(prompt.strip().encode("utf-8")).hexdigest()


def hash_to_int(key: str) -> int:
    """Map a key to an integer for node routing."""
    return int(hashlib.md5(key.encode("utf-8")).hexdigest(), 16)
