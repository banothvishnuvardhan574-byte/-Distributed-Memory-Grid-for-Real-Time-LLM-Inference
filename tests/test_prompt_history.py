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


def test_recent_prompts_supports_limit():
    with main.recent_prompts_lock:
        original_prompts = list(main.recent_prompts)
        main.recent_prompts.clear()
        main.recent_prompts.extend(
            {
                "request_id": f"history-request-{index}",
                "prompt": f"prompt {index}",
                "status": "completed",
                "cache": "miss",
            }
            for index in reversed(range(3))
        )

    try:
        with TestClient(main.app) as client:
            response = client.get(
                "/api/prompts/recent",
                params={"limit": 2},
            )

        assert response.status_code == 200
        assert response.json() == {
            "count": 3,
            "prompts": [
                {
                    "request_id": "history-request-2",
                    "prompt": "prompt 2",
                    "status": "completed",
                    "cache": "miss",
                },
                {
                    "request_id": "history-request-1",
                    "prompt": "prompt 1",
                    "status": "completed",
                    "cache": "miss",
                },
            ],
        }
    finally:
        with main.recent_prompts_lock:
            main.recent_prompts.clear()
            main.recent_prompts.extend(original_prompts)


def test_recent_prompts_supports_offset():
    with main.recent_prompts_lock:
        original_prompts = list(main.recent_prompts)
        main.recent_prompts.clear()
        main.recent_prompts.extend(
            {
                "request_id": f"history-request-{index}",
                "prompt": f"prompt {index}",
                "status": "completed",
                "cache": "miss",
            }
            for index in reversed(range(3))
        )

    try:
        with TestClient(main.app) as client:
            response = client.get(
                "/api/prompts/recent",
                params={"limit": 1, "offset": 1},
            )

        assert response.status_code == 200
        assert response.json() == {
            "count": 3,
            "prompts": [
                {
                    "request_id": "history-request-1",
                    "prompt": "prompt 1",
                    "status": "completed",
                    "cache": "miss",
                }
            ],
        }
    finally:
        with main.recent_prompts_lock:
            main.recent_prompts.clear()
            main.recent_prompts.extend(original_prompts)


def test_recent_prompts_rejects_invalid_pagination():
    with TestClient(main.app) as client:
        invalid_limit = client.get(
            "/api/prompts/recent",
            params={"limit": 0},
        )
        oversized_limit = client.get(
            "/api/prompts/recent",
            params={"limit": 51},
        )
        negative_offset = client.get(
            "/api/prompts/recent",
            params={"offset": -1},
        )

    assert invalid_limit.status_code == 422
    assert oversized_limit.status_code == 422
    assert negative_offset.status_code == 422


def test_recent_prompts_filters_before_pagination():
    with main.recent_prompts_lock:
        original_prompts = list(main.recent_prompts)
        main.recent_prompts.clear()
        main.recent_prompts.extend(
            [
                {
                    "request_id": "completed-3",
                    "prompt": "newest completed",
                    "status": "completed",
                    "cache": "miss",
                },
                {
                    "request_id": "failed-1",
                    "prompt": "failed prompt",
                    "status": "failed",
                    "cache": "miss",
                },
                {
                    "request_id": "completed-2",
                    "prompt": "middle completed",
                    "status": "completed",
                    "cache": "hit",
                },
                {
                    "request_id": "completed-1",
                    "prompt": "oldest completed",
                    "status": "completed",
                    "cache": "miss",
                },
            ]
        )

    try:
        with TestClient(main.app) as client:
            response = client.get(
                "/api/prompts/recent",
                params={
                    "status": "completed",
                    "limit": 1,
                    "offset": 1,
                },
            )

        assert response.status_code == 200
        assert response.json() == {
            "count": 3,
            "prompts": [
                {
                    "request_id": "completed-2",
                    "prompt": "middle completed",
                    "status": "completed",
                    "cache": "hit",
                }
            ],
        }
    finally:
        with main.recent_prompts_lock:
            main.recent_prompts.clear()
            main.recent_prompts.extend(original_prompts)


def test_recent_prompts_rejects_unknown_status():
    with TestClient(main.app) as client:
        response = client.get(
            "/api/prompts/recent",
            params={"status": "running"},
        )

    assert response.status_code == 422
