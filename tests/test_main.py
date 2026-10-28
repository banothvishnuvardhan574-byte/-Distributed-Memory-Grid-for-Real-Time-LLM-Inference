from uuid import UUID

from fastapi.testclient import TestClient

from app.main import app


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