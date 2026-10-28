from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_app_imports_and_home():
    response = client.get("/")
    assert response.status_code == 200 and response.json()["status"] == "ready"


def test_all_grid_endpoints():
    assert client.get("/api/grid/config").status_code == 200
    assert client.get("/api/grid/health").json()["status"] == "healthy"
    assert client.get("/api/grid/stats").status_code == 200
    assert client.post("/api/grid/clear").json()["status"] == "cleared"


def test_prompt_end_to_end():
    client.post("/api/grid/clear")
    payload = {"prompt": "day17 integration"}

    assert client.post("/api/prompt", json=payload).json()["cache"] == "miss"

    second_response = client.post("/api/prompt", json=payload).json()
    assert second_response["cache"] == "hit" and second_response["status"] == "completed"


def test_validation_and_worker_error_paths():
    assert client.post("/api/prompt", json={"prompt": "   "}).status_code == 400
    assert client.post("/api/prompt", json={"prompt": "x" * 5000}).status_code == 422


def test_pdf_rejects_non_pdf():
    response = client.post(
        "/api/pdf/today",
        files={"file": ("note.txt", b"hello", "text/plain")},
    )
    assert response.status_code == 400
