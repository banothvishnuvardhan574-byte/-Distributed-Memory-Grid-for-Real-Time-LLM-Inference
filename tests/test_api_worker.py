from fastapi.testclient import TestClient

import app.main as main


def day10_test_inference(prompt: str) -> str:
    return f"Worker processed: {prompt}"


def test_post_prompt_roundtrips_request_id_through_worker(monkeypatch):
    expected_request_id = "day10-request-roundtrip"
    prompt = "test worker roundtrip"

    monkeypatch.setattr(main, "uuid4", lambda: expected_request_id)
    monkeypatch.setattr(main, "stub_inference", day10_test_inference)

    main.grid_clear()
    try:
        with TestClient(main.app) as client:
            response = client.post(
                "/api/prompt",
                json={"prompt": prompt},
            )

        assert response.status_code == 200

        payload = response.json()
        assert payload["request_id"] == expected_request_id
        assert payload["status"] == "completed"
        assert payload["prompt"] == prompt
        assert payload["response"] == f"Worker processed: {prompt}"
        assert payload["cache"] == "miss"
        assert payload["error"] is None
    finally:
        main.grid_clear()
