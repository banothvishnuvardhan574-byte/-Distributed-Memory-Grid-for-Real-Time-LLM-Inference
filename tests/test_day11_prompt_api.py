from fastapi.testclient import TestClient

import app.main as main


def day11_test_inference(prompt: str) -> str:
    return f"Day 11 processed: {prompt}"


def test_prompt_endpoint_rejects_missing_prompt():
    with TestClient(main.app) as client:
        response = client.post("/api/prompt", json={})

    assert response.status_code == 422


def test_prompt_endpoint_rejects_blank_prompt():
    with TestClient(main.app) as client:
        response = client.post(
            "/api/prompt",
            json={"prompt": "   "},
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Prompt cannot be empty"


def test_prompt_endpoint_returns_expected_response_fields(monkeypatch):
    expected_request_id = "day11-prompt-response-test"
    prompt = "day11 prompt response"

    monkeypatch.setattr(main, "uuid4", lambda: expected_request_id)
    monkeypatch.setattr(main, "stub_inference", day11_test_inference)

    main.grid_clear()
    try:
        with TestClient(main.app) as client:
            response = client.post(
                "/api/prompt",
                json={"prompt": prompt},
            )

        assert response.status_code == 200

        payload = response.json()
        assert set(payload) == {
            "request_id",
            "status",
            "prompt",
            "response",
            "cache",
            "error",
        }
        assert payload["request_id"] == expected_request_id
        assert payload["status"] == "completed"
        assert payload["prompt"] == prompt
        assert payload["response"] == f"Day 11 processed: {prompt}"
        assert payload["cache"] == "miss"
        assert payload["error"] is None
    finally:
        main.grid_clear()
