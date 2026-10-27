from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_empty_prompt_returns_400():
    response = client.post(
        "/api/prompt",
        json={"prompt": ""},
    )

    assert response.status_code == 400


def test_oversized_prompt_returns_422():
    response = client.post(
        "/api/prompt",
        json={"prompt": "a" * 4001},
    )

    assert response.status_code == 422


def test_valid_prompt_returns_200():
    response = client.post(
        "/api/prompt",
        json={"prompt": "Hello MemoryGrid"},
    )

    assert response.status_code == 200
    assert response.json()["status"] == "completed"
    assert response.json()["cache"] in {"hit", "miss"}