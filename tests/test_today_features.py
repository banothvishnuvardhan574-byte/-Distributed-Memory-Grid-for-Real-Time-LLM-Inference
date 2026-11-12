from fastapi.testclient import TestClient

import app.main as main


client = TestClient(main.app)
HEADERS = {"X-API-Key": "test-api-key"}


def test_prompt_requires_api_key():
    response = client.post("/api/prompt", json={"prompt": "missing key"})

    assert response.status_code == 401


def test_prompt_accepts_api_key(monkeypatch):
    monkeypatch.setattr(
        main,
        "run_prompt",
        lambda prompt, request_id: {
            "request_id": request_id,
            "status": "completed",
            "response": "ok",
            "cache": "miss",
            "error": None,
        },
    )
    response = client.post(
        "/api/prompt",
        json={"prompt": "authenticated"},
        headers=HEADERS,
    )

    assert response.status_code == 200


def test_prompt_rate_limit_rejects_requests_after_30(monkeypatch):
    monkeypatch.setattr(
        main,
        "run_prompt",
        lambda prompt, request_id: {
            "request_id": request_id,
            "status": "completed",
            "response": "ok",
            "cache": "miss",
            "error": None,
        },
    )

    responses = [
        client.post(
            "/api/prompt",
            json={"prompt": f"rate limit request {index}"},
            headers=HEADERS,
        )
        for index in range(35)
    ]

    assert [response.status_code for response in responses[:30]] == [200] * 30
    assert [response.status_code for response in responses[30:]] == [429] * 5


def test_jobs_list_filter_and_delete_finished_jobs():
    with main.jobs_lock:
        original_jobs = main.jobs.copy()
        main.jobs.clear()
        main.jobs.update(
            {
                "running-1": {"status": "running", "result": None},
                "completed-1": {"status": "completed", "result": {}},
                "failed-1": {"status": "failed", "result": {}},
            }
        )

    try:
        all_jobs = client.get("/api/jobs", headers=HEADERS)
        completed_jobs = client.get(
            "/api/jobs",
            params={"status": "completed"},
            headers=HEADERS,
        )
        cleared = client.delete("/api/jobs", headers=HEADERS)
        remaining_jobs = client.get("/api/jobs", headers=HEADERS)

        assert all_jobs.status_code == 200
        assert all_jobs.json()["count"] == 3
        assert completed_jobs.json() == {
            "count": 1,
            "jobs": [{"job_id": "completed-1", "status": "completed"}],
        }
        assert cleared.status_code == 200
        assert cleared.json() == {"removed": 2}
        assert remaining_jobs.json() == {
            "count": 1,
            "jobs": [{"job_id": "running-1", "status": "running"}],
        }
    finally:
        with main.jobs_lock:
            main.jobs.clear()
            main.jobs.update(original_jobs)


def test_jobs_list_returns_empty_result_for_unmatched_status():
    with main.jobs_lock:
        original_jobs = main.jobs.copy()
        main.jobs.clear()
        main.jobs["failed-1"] = {"status": "failed", "result": {}}

    try:
        response = client.get(
            "/api/jobs",
            params={"status": "completed"},
            headers=HEADERS,
        )

        assert response.status_code == 200
        assert response.json() == {"count": 0, "jobs": []}
    finally:
        with main.jobs_lock:
            main.jobs.clear()
            main.jobs.update(original_jobs)
