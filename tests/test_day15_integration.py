from fastapi.testclient import TestClient

from app.main import app


def test_app_health_endpoint():
    with TestClient(app) as client:
        response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_home_endpoint():
    with TestClient(app) as client:
        response = client.get("/")

    assert response.status_code == 200
    assert response.json()["status"] == "ready"


def test_prompt_cache_flow_and_grid_stats():
    prompt = "day15 integration"

    with TestClient(app) as client:
        clear_response = client.post("/api/grid/clear")
        assert clear_response.status_code == 200

        try:
            first_response = client.post(
                "/api/prompt",
                json={"prompt": prompt},
            )
            second_response = client.post(
                "/api/prompt",
                json={"prompt": prompt},
            )
            stats_response = client.get("/api/grid/stats")

            assert first_response.status_code == 200
            assert first_response.json()["cache"] == "miss"
            assert second_response.status_code == 200
            assert second_response.json()["cache"] == "hit"
            assert stats_response.status_code == 200

            stats = stats_response.json()
            assert stats["cache_hits"] >= 1
            assert 0.0 <= stats["hit_rate"] <= 1.0
        finally:
            client.post("/api/grid/clear")
