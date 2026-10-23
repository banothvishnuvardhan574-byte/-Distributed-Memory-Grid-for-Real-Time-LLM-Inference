import hashlib
import re


def _normalize_key(value: str) -> str:
    """Collapse repeated whitespace so equivalent strings hash identically."""
    if not isinstance(value, str):
        raise TypeError("value must be a string")
    return re.sub(r"\s+", " ", value).strip()


def hash_prompt(prompt: str) -> str:
    """Return a stable SHA-256 hash of a normalized prompt."""
    normalized = _normalize_key(prompt)
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()


def hash_to_int(key: str) -> int:
    """Map a key to an integer for node routing."""
    normalized = _normalize_key(key)
    return int(hashlib.md5(normalized.encode("utf-8")).hexdigest(), 16)
