from collections import OrderedDict


class LRUPolicy:
    """Track key access order and evict the least-recently-used key."""

    def __init__(self, capacity: int):
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self.capacity = capacity
        self.order: OrderedDict[str, None] = OrderedDict()

    def touch(self, key: str) -> None:
        """Mark a key as most-recently-used (call on get and set)."""
        self.order.pop(key, None)
        self.order[key] = None

    def evict(self) -> str | None:
        """Return and remove the LRU key only when over capacity."""
        if len(self.order) <= self.capacity:
            return None
        oldest, _ = self.order.popitem(last=False)
        return oldest

    def remove(self, key: str) -> None:
        """Forget a key, for example on TTL expiry or manual delete."""
        self.order.pop(key, None)

    def __len__(self) -> int:
        return len(self.order)
