from uuid import uuid4

from fastapi.testclient import TestClient

import app.main as main


client = TestClient(main.app)


def test_metrics_counts_requests_by_endpoint():
    before = client.get("/api/metrics").json()["requests"]

    response = client.get("/health")
    after = client.get("/api/metrics").json()["requests"]

    assert response.status_code == 200
    assert after["total"] == before["total"] + 2
    assert after["by_endpoint"]["/health"] == (
        before["by_endpoint"].get("/health", 0) + 1
    )
    assert after["by_endpoint"]["/api/metrics"] == (
        before["by_endpoint"].get("/api/metrics", 0) + 1
    )


def test_metrics_reports_cache_and_job_totals():
    main.grid_clear()
    prompt = f"metrics cache test {uuid4()}"
    first = client.post("/api/prompt", json={"prompt": prompt})
    second = client.post("/api/prompt", json={"prompt": prompt})
    assert first.json()["cache"] == "miss"
    assert second.json()["cache"] == "hit"

    response = client.get("/api/metrics")

    assert response.status_code == 200
    assert response.json()["cache"] == {"hits": 1, "misses": 1}
    with main.jobs_lock:
        expected_job_count = len(main.jobs)
    assert response.json()["jobs"] == {"total": expected_job_count}
