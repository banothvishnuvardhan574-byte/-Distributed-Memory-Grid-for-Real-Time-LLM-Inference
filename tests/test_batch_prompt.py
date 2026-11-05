from uuid import uuid4

from fastapi.testclient import TestClient

import app.main as main


client = TestClient(main.app)


def test_batch_prompts_report_cache_misses_and_hits():
    main.grid_clear()
    prompt = f"batch cache test {uuid4()}"

    response = client.post(
        "/api/prompts/batch",
        json={"prompts": [prompt, prompt, "   "]},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 2
    assert [result["cache"] for result in body["results"]] == ["miss", "hit"]
    assert body["results"][0]["response"] == body["results"][1]["response"]
    assert body["results"][0]["request_id"] != body["results"][1]["request_id"]


def test_batch_prompts_validates_prompt_count():
    assert client.post("/api/prompts/batch", json={"prompts": []}).status_code == 422
    response = client.post(
        "/api/prompts/batch",
        json={"prompts": ["prompt"] * 21},
    )
    assert response.status_code == 422
