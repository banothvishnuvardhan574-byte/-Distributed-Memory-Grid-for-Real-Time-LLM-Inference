import pytest

from app.grid.memory_grid import MemoryGrid


def test_grid_routes_set_and_get_to_the_same_node():
    grid = MemoryGrid(node_count=4)
    key = "shared prompt"

    grid.set(key, "response")

    assert grid.get(key) == "response"
    assert sum(node["entries"] for node in grid.stats()) == 1


def test_grid_stats_reports_all_nodes():
    grid = MemoryGrid(node_count=3, capacity_per_node=7)

    assert grid.stats() == [
        {"node_id": 0, "entries": 0, "capacity": 7, "alive": True},
        {"node_id": 1, "entries": 0, "capacity": 7, "alive": True},
        {"node_id": 2, "entries": 0, "capacity": 7, "alive": True},
    ]


def test_grid_rejects_invalid_node_count():
    with pytest.raises(ValueError, match="node_count must be positive"):
        MemoryGrid(node_count=0)



def test_grid_evicts_lru_key_on_target_node():
    grid = MemoryGrid(node_count=1, capacity_per_node=2)

    grid.set("a", "1")
    grid.set("b", "2")
    assert grid.get("a") == "1"  # Refresh a's LRU position
    grid.set("c", "3")           # b should be evicted

    assert grid.get("a") == "1"
    assert grid.get("b") is None
    assert grid.get("c") == "3"
    assert grid.stats()[0]["entries"] == 2
