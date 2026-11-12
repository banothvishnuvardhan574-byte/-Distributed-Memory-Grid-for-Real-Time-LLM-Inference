from fastapi.testclient import TestClient

import app.main as main


client = TestClient(main.app)


def test_prompt_rejects_missing_or_invalid_api_key():
    missing_key = client.post("/api/prompt", json={"prompt": "hello"})
    invalid_key = client.post(
        "/api/prompt",
        json={"prompt": "hello"},
        headers={"X-API-Key": "invalid-key"},
    )

    assert missing_key.status_code == 401
    assert invalid_key.status_code == 401


def test_prompt_accepts_configured_api_key():
    response = client.post(
        "/api/prompt",
        json={"prompt": "authenticated prompt"},
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 200


def test_async_job_submission_rejects_missing_or_invalid_api_key():
    missing_key = client.post("/api/jobs", json={"prompt": "hello"})
    invalid_key = client.post(
        "/api/jobs",
        json={"prompt": "hello"},
        headers={"X-API-Key": "invalid-key"},
    )

    assert missing_key.status_code == 401
    assert invalid_key.status_code == 401


def test_async_job_submission_accepts_configured_api_key():
    response = client.post(
        "/api/jobs",
        json={"prompt": "authenticated async prompt"},
        headers={"X-API-Key": "test-api-key"},
    )

    assert response.status_code == 202


def test_async_job_management_requires_api_key():
    responses = [
        client.get("/api/jobs"),
        client.get("/api/jobs/nonexistent"),
        client.delete("/api/jobs"),
    ]

    assert [response.status_code for response in responses] == [401, 401, 401]


def test_prompt_rate_limit_is_per_key(monkeypatch):
    monkeypatch.setattr(main, "RATE_LIMIT", 2)
    monkeypatch.setattr(
        main,
        "API_KEYS",
        {"test-api-key", "another-test-key"},
    )

    headers = {"X-API-Key": "test-api-key"}
    first = client.post(
        "/api/prompt",
        json={"prompt": "first"},
        headers=headers,
    )
    second = client.post(
        "/api/prompt",
        json={"prompt": "second"},
        headers=headers,
    )
    limited = client.post("/api/prompt", json={"prompt": "third"}, headers=headers)
    another_key = client.post(
        "/api/prompt",
        json={"prompt": "another key"},
        headers={"X-API-Key": "another-test-key"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert limited.status_code == 429
    assert limited.json()["detail"] == "Rate limit exceeded"
    assert another_key.status_code == 200


def test_async_job_submission_uses_configured_rate_limit(monkeypatch):
    monkeypatch.setattr(main, "RATE_LIMIT", 1)
    headers = {"X-API-Key": "test-api-key"}

    accepted = client.post(
        "/api/jobs",
        json={"prompt": "first async prompt"},
        headers=headers,
    )
    limited = client.post(
        "/api/jobs",
        json={"prompt": "second async prompt"},
        headers=headers,
    )

    assert accepted.status_code == 202
    assert limited.status_code == 429
    assert limited.json()["detail"] == "Rate limit exceeded"
