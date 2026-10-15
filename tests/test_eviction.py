import pytest

from app.grid.eviction import LRUPolicy


def test_no_eviction_under_capacity():
    policy = LRUPolicy(capacity=3)
    for key in ("a", "b", "c"):
        policy.touch(key)
    assert policy.evict() is None


def test_evicts_oldest_key():
    policy = LRUPolicy(capacity=2)
    policy.touch("a")
    policy.touch("b")
    policy.touch("c")
    assert policy.evict() == "a"


def test_touch_refreshes_key():
    policy = LRUPolicy(capacity=2)
    policy.touch("a")
    policy.touch("b")
    policy.touch("a")
    policy.touch("c")
    assert policy.evict() == "b"


def test_remove_forgets_key():
    policy = LRUPolicy(capacity=2)
    policy.touch("a")
    policy.touch("b")
    policy.remove("a")
    policy.touch("c")
    policy.touch("d")
    assert policy.evict() == "b"


def test_invalid_capacity_raises():
    with pytest.raises(ValueError):
        LRUPolicy(capacity=0)


def test_negative_capacity_raises():
    with pytest.raises(ValueError):
        LRUPolicy(capacity=-1)
