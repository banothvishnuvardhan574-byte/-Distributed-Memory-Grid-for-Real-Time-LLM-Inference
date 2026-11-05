from concurrent.futures import ThreadPoolExecutor
import threading
import time
from uuid import uuid4

from fastapi.testclient import TestClient

import app.main as main
from app.main import app


client = TestClient(app)


def _wait_for_job(job_id: str) -> dict:
    deadline = time.monotonic() + 5
    while time.monotonic() < deadline:
        response = client.get(f"/api/jobs/{job_id}")
        assert response.status_code == 200
        job = response.json()
        if job["status"] != "running":
            return job
        time.sleep(0.05)

    raise AssertionError(f"Job {job_id} did not finish within five seconds")


def test_job_lifecycle():
    response = client.post(
        "/api/jobs",
        json={"prompt": f"day21 lifecycle {uuid4()}"},
    )

    assert response.status_code == 202
    job_id = response.json()["job_id"]
    assert response.json()["status"] == "running"

    job = _wait_for_job(job_id)
    assert job["status"] == "completed"
    assert job["result"]["response"]


def test_job_submission_returns_before_inference_finishes(monkeypatch):
    inference_started = threading.Event()
    release_inference = threading.Event()

    def wait_for_release(prompt: str, request_id: str) -> dict:
        inference_started.set()
        if not release_inference.wait(timeout=5):
            raise TimeoutError("Test did not release the inference worker")
        return {
            "request_id": request_id,
            "status": "completed",
            "response": "finished",
            "cache": "miss",
            "error": None,
        }

    monkeypatch.setattr(main, "run_prompt", wait_for_release)
    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(
        client.post,
        "/api/jobs",
        json={"prompt": f"day21 nonblocking {uuid4()}"},
    )
    job_id: str | None = None

    try:
        assert inference_started.wait(timeout=2)
        response = future.result(timeout=2)
        assert response.status_code == 202
        job_id = response.json()["job_id"]
        assert client.get(f"/api/jobs/{job_id}").json()["status"] == "running"
    finally:
        release_inference.set()
        executor.shutdown(wait=True)

    assert job_id is not None
    assert _wait_for_job(job_id)["status"] == "completed"


def test_job_reports_worker_failure(monkeypatch):
    def fail_prompt(prompt: str, request_id: str) -> dict:
        raise RuntimeError("test worker failure")

    monkeypatch.setattr(main, "run_prompt", fail_prompt)
    response = client.post("/api/jobs", json={"prompt": "day21 failure"})

    assert response.status_code == 202
    job = _wait_for_job(response.json()["job_id"])
    assert job["status"] == "failed"
    assert job["result"]["error"] == "Prompt processing failed"


def test_job_not_found():
    assert client.get("/api/jobs/nonexistent").status_code == 404


def test_job_empty_prompt():
    response = client.post("/api/jobs", json={"prompt": "  "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Prompt cannot be empty"


def test_pdf_search_finds_cached_text_case_insensitively():
    key = f"pdf:day21-search:{uuid4()}"
    text = "The MemoryGrid stores extracted PDF text for later searches."
    main.grid.set(key, text)

    response = client.get("/api/pdf/search", params={"q": "memorygrid"})

    assert response.status_code == 200
    assert response.json() == {
        "query": "memorygrid",
        "matches": 1,
        "results": [{"key": key, "snippet": text}],
    }


def test_pdf_search_empty_query():
    response = client.get("/api/pdf/search", params={"q": " "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Query cannot be empty"
