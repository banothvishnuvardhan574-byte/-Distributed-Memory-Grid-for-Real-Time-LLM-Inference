import time

from app.core.config import settings
from app.grid.eviction import LRUPolicy


class MemoryNode:
    """Store key/value pairs with TTL expiration and LRU eviction."""

    def __init__(self, node_id: int, capacity: int | None = None):
        self.node_id = node_id
        self.capacity = (
            capacity if capacity is not None else settings.cache_size_per_node
        )
        if self.capacity <= 0:
            raise ValueError("capacity must be positive")

        self.store: dict[str, tuple[str, float]] = {}
        self.policy = LRUPolicy(self.capacity)
        self.alive = True

    def set(self, key: str, value: str, ttl: int | None = None) -> None:
        duration = ttl if ttl is not None else settings.default_ttl_seconds
        if duration < 0:
            raise ValueError("ttl cannot be negative")

        expiry = time.time() + duration
        self.store[key] = (value, expiry)
        self.policy.touch(key)
        evicted = self.policy.evict()
        if evicted is not None:
            self.store.pop(evicted, None)

    def get(self, key: str) -> str | None:
        item = self.store.get(key)
        if item is None:
            return None

        value, expiry = item
        if time.time() >= expiry:
            self.store.pop(key, None)
            self.policy.remove(key)
            return None

        self.policy.touch(key)
        return value

    def delete(self, key: str) -> bool:
        removed = self.store.pop(key, None) is not None
        self.policy.remove(key)
        return removed

    def clear(self) -> None:
        self.store.clear()
        self.policy.clear()

    def stats(self) -> dict[str, int | bool]:
        return {
            "node_id": self.node_id,
            "entries": len(self.store),
            "capacity": self.capacity,
            "alive": self.alive,
        }
