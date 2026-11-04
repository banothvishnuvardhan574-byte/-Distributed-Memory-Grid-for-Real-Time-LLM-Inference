import time

import pytest

from app.grid.memory_node import MemoryNode


def test_set_and_get():
    node = MemoryNode(node_id=0, capacity=10)
    node.set("k", "v")

    assert node.get("k") == "v"


def test_missing_key_returns_none():
    node = MemoryNode(node_id=0, capacity=10)

    assert node.get("nope") is None


def test_expired_key_returns_none():
    node = MemoryNode(node_id=0, capacity=10)
    node.set("k", "v", ttl=0)
    time.sleep(0.01)

    assert node.get("k") is None
    assert len(node.store) == 0


def test_evicts_lru_when_over_capacity():
    node = MemoryNode(node_id=0, capacity=2)
    node.set("a", "1")
    node.set("b", "2")
    node.get("a")
    node.set("c", "3")

    assert node.get("b") is None
    assert node.get("a") == "1"
    assert node.get("c") == "3"


def test_lru_eviction_stays_within_capacity_under_load():
    node = MemoryNode(node_id=0, capacity=7)

    for index in range(1000):
        node.set(f"key-{index}", str(index))

    assert len(node.store) == 7
    assert len(node.policy) == 7
    assert [node.get(f"key-{index}") for index in range(993, 1000)] == [
        str(index) for index in range(993, 1000)
    ]
    assert node.get("key-992") is None


def test_expiration_at_ttl_boundary_removes_key_and_lru_entry(monkeypatch):
    now = [100.0]
    monkeypatch.setattr("app.grid.memory_node.time.time", lambda: now[0])
    node = MemoryNode(node_id=0, capacity=2)
    node.set("expires", "value", ttl=5)

    now[0] = 105.0

    assert node.get("expires") is None
    assert "expires" not in node.store
    assert len(node.policy) == 0


def test_delete():
    node = MemoryNode(node_id=0, capacity=10)
    node.set("k", "v")

    assert node.delete("k") is True
    assert node.get("k") is None
    assert node.delete("k") is False


def test_stats():
    node = MemoryNode(node_id=1, capacity=5)
    node.set("k", "v")

    assert node.stats() == {
        "node_id": 1,
        "entries": 1,
        "capacity": 5,
        "alive": True,
    }


def test_invalid_capacity():
    with pytest.raises(ValueError, match="capacity must be positive"):
        MemoryNode(node_id=0, capacity=0)


def test_negative_capacity():
    with pytest.raises(ValueError, match="capacity must be positive"):
        MemoryNode(node_id=0, capacity=-1)


def test_negative_ttl():
    node = MemoryNode(node_id=0, capacity=10)

    with pytest.raises(ValueError, match="ttl cannot be negative"):
        node.set("k", "v", ttl=-1)
