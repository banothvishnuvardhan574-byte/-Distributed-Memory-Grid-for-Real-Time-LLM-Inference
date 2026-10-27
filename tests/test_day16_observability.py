from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_grid_health_reports_expected_fields():
    response = client.get("/api/grid/health")

    assert response.status_code == 200

    body = response.json()
    assert body["status"] == "healthy"
    assert body["node_count"] >= 1
    assert "total_cached_entries" in body
    assert "capacity_per_node" in body
