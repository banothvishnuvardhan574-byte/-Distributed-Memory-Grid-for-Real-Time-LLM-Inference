from fastapi.testclient import TestClient

from app.core.config import settings
from app.grid.memory_grid import MemoryGrid
from app.main import app

 member1-day13-capacity-fix
client = TestClient(app)
    assert len(memory_grid.nodes) == 2
    assert [node.capacity for node in memory_grid.nodes] == [5, 5]
imain


def test_grid_capacity_uses_configured_setting():
    test_grid = MemoryGrid(
        node_count=settings.node_count,
        capacity_per_node=settings.cache_size_per_node,
    )

    assert len(test_grid.nodes) == settings.node_count

    for node in test_grid.nodes:
        assert node.capacity == settings.cache_size_per_node
 member1-day13-capacity-fix

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

    assert response.status_code == 200

    body = response.json()

    assert body == {
        "node_count": settings.node_count,
        "cache_size_per_node": settings.cache_size_per_node,
        "default_ttl_seconds": settings.default_ttl_seconds,
    }

    assert body["node_count"] >= 1
    assert body["cache_size_per_node"] >= 1
    assert body["default_ttl_seconds"] >= 1
 main
