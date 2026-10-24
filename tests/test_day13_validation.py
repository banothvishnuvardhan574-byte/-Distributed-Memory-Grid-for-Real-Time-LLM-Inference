from fastapi.testclient import TestClient

from app.grid.memory_grid import MemoryGrid
from app.main import app

client = TestClient(app)


def test_capacity_applied_to_nodes():
    grid = MemoryGrid(node_count=2, capacity_per_node=5)

    assert all(node.capacity == 5 for node in grid.nodes)


def test_empty_prompt_rejected():
    response = client.post("/api/prompt", json={"prompt": ""})

    assert response.status_code == 422


def test_oversized_prompt_rejected():
    response = client.post("/api/prompt", json={"prompt": "x" * 5000})

    assert response.status_code == 422


def test_valid_prompt_accepted():
    response = client.post("/api/prompt", json={"prompt": "day13 check"})

    assert response.status_code == 200
    assert response.json()["cache"] in {"hit", "miss"}
