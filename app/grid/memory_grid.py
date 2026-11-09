import re

from app.grid.memory_node import MemoryNode
from app.grid.router import GridRouter


def _normalize_key(value: str) -> str:
    """Collapse repeated whitespace so equivalent cache keys land in the same slot."""
    if not isinstance(value, str):
        raise TypeError("key must be a string")
    return re.sub(r"\s+", " ", value).strip()


class MemoryGrid:
    """Coordinate key routing and cache operations across memory nodes."""

    def __init__(self, node_count: int, capacity_per_node: int | None = None):
        self.router = GridRouter(node_count=node_count)
        self.nodes = [
            MemoryNode(node_id=node_id, capacity=capacity_per_node)
            for node_id in range(node_count)
        ]

    def get(self, key: str) -> str | None:
        normalized_key = _normalize_key(key)
        return self.nodes[self.router.route(normalized_key)].get(normalized_key)

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        normalized_key = _normalize_key(key)
        self.nodes[self.router.route(normalized_key)].set(normalized_key, value, ttl=ttl)

    def stats(self) -> list[dict[str, int | bool]]:
        return [node.stats() for node in self.nodes]
