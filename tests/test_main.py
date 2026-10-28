import time
from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app
import app.main as main


client = TestClient(app)


def test_home_returns_ready_status():
    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "LLM MemoryGrid API is running",
        "status": "ready",
    }


def test_health_check_returns_healthy_status():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_submit_prompt_trims_prompt_and_returns_request_id():
    response = client.post("/api/prompt", json={"prompt": "  hello  "})

    assert response.status_code == 200
    response_body = response.json()
    assert response_body["status"] == "accepted"
    assert response_body["prompt"] == "hello"
    UUID(response_body["request_id"])


def test_submit_prompt_rejects_empty_prompt():
    response = client.post("/api/prompt", json={"prompt": "  "})

    assert response.status_code == 400
    assert response.json()["detail"] == "Prompt cannot be empty"


def test_prompt_acceptance_inputs_and_cache_behavior():
    cases = [
        ("normal", "Explain what a cache is.", 200),
        ("repeat", "Explain what a cache is.", 200),
        ("empty", "", 400),
        ("whitespace", "   \t  ", 400),
        ("special characters", "Special chars: !@#$%^&*()_+-=[]{};':\",./<>?", 200),
        ("separate prompt A", "Describe a blue ocean.", 200),
        ("separate prompt B", "Describe a quiet forest.", 200),
    ]

    main.grid_clear()
    measured_results = []

    try:
        responses = {}
        for name, prompt, expected_status in cases:
            started = time.perf_counter()
            response = client.post("/api/prompt", json={"prompt": prompt})
            elapsed_ms = (time.perf_counter() - started) * 1000
            measured_results.append((name, response.status_code, elapsed_ms))
            assert response.status_code == expected_status
            responses[name] = response.json()

        assert responses["normal"]["prompt"] == "Explain what a cache is."
        assert responses["normal"]["response"] == "[stub] echo: Explain what a cache is."
        assert responses["normal"]["cache"] == "miss"
        assert responses["repeat"]["cache"] == "hit"
        assert responses["repeat"]["response"] == responses["normal"]["response"]
        assert responses["empty"]["detail"] == "Prompt cannot be empty"
        assert responses["whitespace"]["detail"] == "Prompt cannot be empty"
        assert responses["special characters"]["cache"] == "miss"
        assert responses["separate prompt A"]["cache"] == "miss"
        assert responses["separate prompt B"]["cache"] == "miss"

        stats = main.grid_stats()
        assert stats["cache_hits"] == 1
        assert stats["cache_misses"] == 4
        assert stats["hit_rate"] == 0.2
    finally:
        main.grid_clear()

    print("Measured TestClient request times (ms):")
    for name, status_code, elapsed_ms in measured_results:
        print(f"{name}: HTTP {status_code}, {elapsed_ms:.2f} ms")