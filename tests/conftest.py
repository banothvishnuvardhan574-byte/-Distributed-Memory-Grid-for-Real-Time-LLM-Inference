import pytest

import app.main as main


def fake_test_inference(prompt: str) -> str:
    """Deterministic inference response for automated API tests."""
    return f"[stub] echo: {prompt[:200]}"


@pytest.fixture(autouse=True)
def isolate_test_inference(monkeypatch):
    """Use fake inference and clean up the worker after every test."""
    monkeypatch.setattr(
        main,
        "stub_inference",
        fake_test_inference,
    )

    main.grid_clear()

    yield

    main.shutdown_worker()
    main.grid_clear()