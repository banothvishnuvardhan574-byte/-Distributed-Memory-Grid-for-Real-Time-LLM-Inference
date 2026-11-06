from fastapi.testclient import TestClient

import app.main as main


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
            response = client.get("/api/jobs", params={"limit": 2})

        assert response.status_code == 200
        assert response.json() == {
            "count": 2,
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

    assert too_small.status_code == 422
    assert too_large.status_code == 422
