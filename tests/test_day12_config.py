from fastapi.testclient import TestClient

from app.core.config import settings
from app.grid.memory_grid import MemoryGrid
from app.main import app

client = TestClient(app)


def test_grid_capacity_uses_configured_setting():
    test_grid = MemoryGrid(
        node_count=settings.node_count,
        capacity_per_node=settings.cache_size_per_node,
    )

    assert len(test_grid.nodes) == settings.node_count

    for node in test_grid.nodes:
        assert node.capacity == settings.cache_size_per_node


def test_grid_config_endpoint():
    response = client.get("/api/grid/config")

    assert response.status_code == 200

    data = response.json()
    assert data["node_count"] == settings.node_count
    assert data["cache_size_per_node"] == settings.cache_size_per_node
    assert data["default_ttl_seconds"] == settings.default_ttl_seconds


def test_grid_stats_endpoint():
    response = client.get("/api/grid/stats")

    assert response.status_code == 200

    data = response.json()
    assert "nodes" in data
    assert "cache_hits" in data
    assert "cache_misses" in data
    assert "hit_rate" in data


def test_grid_clear_endpoint():
    response = client.post("/api/grid/clear")

    assert response.status_code == 200
    assert response.json()["status"] == "cleared"
