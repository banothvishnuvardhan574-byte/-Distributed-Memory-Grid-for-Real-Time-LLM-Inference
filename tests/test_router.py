import pytest

from app.grid.router import GridRouter


def test_route_is_deterministic():
    router = GridRouter(node_count=4)
    assert router.route("key1") == router.route("key1")


def test_route_within_node_range():
    router = GridRouter(node_count=4)
    for i in range(50):
        node_id = router.route(f"key-{i}")
        assert 0 <= node_id < 4


def test_routes_distributed_across_nodes():
    router = GridRouter(node_count=4)
    nodes = {router.route(f"key-{i}") for i in range(100)}
    assert len(nodes) > 1


def test_route_many():
    router = GridRouter(node_count=4)
    result = router.route_many(["a", "b", "c"])
    assert result == {key: router.route(key) for key in ("a", "b", "c")}


def test_empty_key_raises():
    router = GridRouter(node_count=4)
    with pytest.raises(ValueError, match="key cannot be empty"):
        router.route("")


@pytest.mark.parametrize("node_count", [0, -1])
def test_invalid_node_count_raises(node_count):
    with pytest.raises(ValueError, match="node_count must be positive"):
        GridRouter(node_count=node_count)
