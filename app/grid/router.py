import re

from app.core.hashing import hash_to_int


def _normalize_key(value: str) -> str:
    """Collapse repeated whitespace and trim so equivalent keys route identically."""
    if not isinstance(value, str):
        raise TypeError("key must be a string")
    return re.sub(r"\s+", " ", value).strip()


class GridRouter:
    """Deterministically map cache keys to node ids using hash routing."""

    def __init__(self, node_count: int):
        if node_count <= 0:
            raise ValueError("node_count must be positive")
        self.node_count = node_count

    def route(self, key: str) -> int:
        """Return the node id responsible for this key."""
        normalized_key = _normalize_key(key)
        if not normalized_key:
            raise ValueError("key cannot be empty")
        return hash_to_int(normalized_key) % self.node_count

    def route_many(self, keys: list[str]) -> dict[str, int]:
        """Map multiple keys to their node ids."""
        return {key: self.route(key) for key in keys}
