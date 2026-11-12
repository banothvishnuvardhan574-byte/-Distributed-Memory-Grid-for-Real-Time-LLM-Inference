from fastapi.testclient import TestClient

import app.main as main


HEADERS = {"X-API-Key": "test-api-key"}


def test_list_jobs_returns_latest_jobs_first_and_respects_limit():
    with main.jobs_lock:
        original_jobs = main.jobs.copy()
        main.jobs.clear()
        main.jobs.update(
            {
                "job-1": {"status": "completed", "result": {"response": "one"}},
                "job-2": {"status": "running", "result": None},
                "job-3": {"status": "failed", "result": {"error": "failed"}},
            }
        )

    try:
        with TestClient(main.app) as client:
            response = client.get(
                "/api/jobs",
                params={"limit": 2},
                headers=HEADERS,
            )

        assert response.status_code == 200
        assert response.json() == {
            "count": 3,
            "jobs": [
                {"job_id": "job-3", "status": "failed"},
                {"job_id": "job-2", "status": "running"},
            ],
        }
    finally:
        with main.jobs_lock:
            main.jobs.clear()
            main.jobs.update(original_jobs)


def test_list_jobs_rejects_out_of_range_limit():
    with TestClient(main.app) as client:
        too_small = client.get("/api/jobs", params={"limit": 0})
        too_large = client.get("/api/jobs", params={"limit": 101})
        negative_offset = client.get("/api/jobs", params={"offset": -1})

    assert too_small.status_code == 422
    assert too_large.status_code == 422
    assert negative_offset.status_code == 422


def test_list_jobs_rejects_unknown_status():
    with TestClient(main.app) as client:
        response = client.get(
            "/api/jobs",
            params={"status": "queued"},
            headers=HEADERS,
        )

    assert response.status_code == 422


def test_list_jobs_filters_by_status_before_applying_limit():
    with main.jobs_lock:
        original_jobs = main.jobs.copy()
        main.jobs.clear()
        main.jobs.update(
            {
                "completed-1": {"status": "completed", "result": None},
                "completed-2": {"status": "completed", "result": None},
                "failed-1": {"status": "failed", "result": None},
            }
        )

    try:
        with TestClient(main.app) as client:
            response = client.get(
                "/api/jobs",
                params={"status": "completed", "limit": 1},
                headers=HEADERS,
            )

        assert response.status_code == 200
        assert response.json() == {
            "count": 2,
            "jobs": [{"job_id": "completed-2", "status": "completed"}],
        }
    finally:
        with main.jobs_lock:
            main.jobs.clear()
            main.jobs.update(original_jobs)


def test_list_jobs_applies_offset_after_status_filtering():
    with main.jobs_lock:
        original_jobs = main.jobs.copy()
        main.jobs.clear()
        main.jobs.update(
            {
                "completed-1": {"status": "completed", "result": None},
                "failed-1": {"status": "failed", "result": None},
                "completed-2": {"status": "completed", "result": None},
                "completed-3": {"status": "completed", "result": None},
            }
        )

    try:
        with TestClient(main.app) as client:
            response = client.get(
                "/api/jobs",
                params={"status": "completed", "limit": 1, "offset": 1},
                headers=HEADERS,
            )

        assert response.status_code == 200
        assert response.json() == {
            "count": 3,
            "jobs": [{"job_id": "completed-2", "status": "completed"}],
        }
    finally:
        with main.jobs_lock:
            main.jobs.clear()
            main.jobs.update(original_jobs)


def test_clear_finished_jobs_keeps_running_jobs():
    with main.jobs_lock:
        original_jobs = main.jobs.copy()
        main.jobs.clear()
        main.jobs.update(
            {
                "completed-1": {"status": "completed", "result": None},
                "running-1": {"status": "running", "result": None},
                "failed-1": {"status": "failed", "result": None},
            }
        )

    try:
        with TestClient(main.app) as client:
            deleted = client.delete("/api/jobs", headers=HEADERS)
            remaining = client.get("/api/jobs", headers=HEADERS)

        assert deleted.status_code == 200
        assert deleted.json() == {"removed": 2}
        assert remaining.json() == {
            "count": 1,
            "jobs": [{"job_id": "running-1", "status": "running"}],
        }
    finally:
        with main.jobs_lock:
            main.jobs.clear()
            main.jobs.update(original_jobs)
