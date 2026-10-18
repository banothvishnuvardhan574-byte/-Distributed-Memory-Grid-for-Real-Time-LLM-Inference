from uuid import UUID

import pytest
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


@pytest.mark.parametrize("prompt", ["", "  "])
def test_submit_prompt_rejects_empty_or_whitespace_only_prompt(prompt):
    response = client.post("/api/prompt", json={"prompt": prompt})

    assert response.status_code == 400
    assert response.json()["detail"] == "Prompt cannot be empty"


@pytest.mark.parametrize(
    ("payload", "expected_message"),
    [
        ({}, "Field required"),
        ({"prompt": 123}, "Input should be a valid string"),
        ({"prompt": None}, "Input should be a valid string"),
    ],
)
def test_submit_prompt_rejects_missing_or_malformed_input(payload, expected_message):
    response = client.post("/api/prompt", json=payload)

    assert response.status_code == 422
    assert response.json()["detail"][0]["loc"][-1] == "prompt"
    assert expected_message in response.json()["detail"][0]["msg"]
