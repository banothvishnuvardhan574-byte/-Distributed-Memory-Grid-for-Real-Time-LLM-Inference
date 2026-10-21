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
