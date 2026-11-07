from fastapi.testclient import TestClient

import app.main as main


def test_recent_prompts_lists_prompt_with_cache_status(monkeypatch):
    request_id = "history-request-1"
    prompt = "remember this prompt"

    monkeypatch.setattr(main, "uuid4", lambda: request_id)
    monkeypatch.setattr(
        main,
        "run_prompt",
        lambda value, identifier: {
            "request_id": identifier,
            "status": "completed",
            "response": "done",
            "cache": "hit",
            "error": None,
        },
    )
    with main.recent_prompts_lock:
        main.recent_prompts.clear()

    try:
        with TestClient(
            main.app,
            headers={"X-API-Key": "test-api-key"},
        ) as client:
            response = client.post(
                "/api/prompt",
                json={"prompt": prompt},
            )
            history = client.get("/api/prompts/recent")

        assert response.status_code == 200
        assert history.status_code == 200
        assert history.json() == {
            "count": 1,
            "prompts": [
                {
                    "request_id": request_id,
                    "prompt": prompt,
                    "status": "completed",
                    "cache": "hit",
                }
            ],
        }
    finally:
        with main.recent_prompts_lock:
            main.recent_prompts.clear()


def test_recent_prompts_keeps_only_latest_50(monkeypatch):
    monkeypatch.setattr(main, "RATE_LIMIT", 60)
    request_ids = iter(f"history-request-{index}" for index in range(51))
    monkeypatch.setattr(main, "uuid4", lambda: next(request_ids))
    monkeypatch.setattr(
        main,
        "run_prompt",
        lambda prompt, request_id: {
            "request_id": request_id,
            "status": "completed",
            "response": "done",
            "cache": "miss",
            "error": None,
        },
    )
    with main.recent_prompts_lock:
        main.recent_prompts.clear()

    try:
        with TestClient(
            main.app,
            headers={"X-API-Key": "test-api-key"},
        ) as client:
            for index in range(51):
                response = client.post(
                    "/api/prompt",
                    json={"prompt": f"prompt {index}"},
                )
                assert response.status_code == 200

            history = client.get("/api/prompts/recent").json()

        assert history["count"] == 50
        assert history["prompts"][0]["request_id"] == "history-request-50"
        assert history["prompts"][-1]["request_id"] == "history-request-1"
    finally:
        with main.recent_prompts_lock:
            main.recent_prompts.clear()
