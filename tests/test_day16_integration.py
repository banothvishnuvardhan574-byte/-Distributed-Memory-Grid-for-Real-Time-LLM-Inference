from uuid import uuid4

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_grid_health_endpoint():
    response = client.get("/api/grid/health")

    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "healthy"
    assert body["node_count"] >= 1


def test_prompt_flow_after_health():
    client.post("/api/grid/clear")
    prompt = {"prompt": f"day16 integration {uuid4()}"}

    first_response = client.post("/api/prompt", json=prompt)
    second_response = client.post("/api/prompt", json=prompt)

    assert first_response.status_code == 200
    assert first_response.json()["cache"] == "miss"
    assert second_response.status_code == 200
    assert second_response.json()["cache"] == "hit"

    client.post("/api/grid/clear")
