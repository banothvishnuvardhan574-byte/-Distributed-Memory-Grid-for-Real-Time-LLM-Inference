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
