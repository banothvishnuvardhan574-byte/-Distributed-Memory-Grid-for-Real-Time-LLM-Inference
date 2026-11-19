from fastapi.testclient import TestClient

import app.main as main


client = TestClient(main.app)


def test_prompt_accepts_requests_without_api_key():
    missing_key = client.post("/api/prompt", json={"prompt": "hello"})
    assert missing_key.status_code == 200


def test_prompt_accepts_configured_api_key_for_backward_compatibility():
    response = client.post(
        "/api/prompt",
        json={"prompt": "authenticated prompt"},
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 200


def test_async_job_submission_accepts_requests_without_api_key():
    missing_key = client.post("/api/jobs", json={"prompt": "hello"})
    assert missing_key.status_code == 202


def test_async_job_submission_accepts_configured_api_key():
    response = client.post(
        "/api/jobs",
        json={"prompt": "authenticated async prompt"},
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 202


def test_async_job_management_is_public():
    responses = [
        client.get("/api/jobs"),
        client.get("/api/jobs/nonexistent"),
        client.delete("/api/jobs"),
    ]

    assert [response.status_code for response in responses] == [200, 404, 200]


def test_prompt_requests_are_not_rate_limited_by_api_key():
    responses = [
        client.post("/api/prompt", json={"prompt": f"prompt {index}"})
        for index in range(4)
    ]
    assert [response.status_code for response in responses] == [200, 200, 200, 200]


def test_async_jobs_allow_multiple_submissions():
    responses = [
        client.post("/api/jobs", json={"prompt": f"async prompt {index}"})
        for index in range(2)
    ]
    assert [response.status_code for response in responses] == [202, 202]
