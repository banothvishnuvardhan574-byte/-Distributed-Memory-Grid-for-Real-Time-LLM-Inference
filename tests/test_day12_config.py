from fastapi.testclient import TestClient

from app.core.config import settings
from app.grid.memory_grid import MemoryGrid
from app.main import app, grid


def test_memory_grid_applies_capacity_to_every_node():
    memory_grid = MemoryGrid(node_count=2, capacity_per_node=5)

    assert [node.capacity for node in memory_grid.nodes] == [5, 5]


def test_application_grid_uses_configured_capacity():
    assert all(
        node.capacity == settings.cache_size_per_node
        for node in grid.nodes
    )


def test_grid_config_endpoint_returns_active_settings():
    with TestClient(app) as client:
        response = client.get("/api/grid/config")

    assert response.status_code == 200
    assert response.json() == {
        "node_count": settings.node_count,
        "cache_size_per_node": settings.cache_size_per_node,
        "default_ttl_seconds": settings.default_ttl_seconds,
    }
