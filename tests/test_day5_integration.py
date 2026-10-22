
from uuid import uuid4

from app.core.config import settings
import pytest
from fastapi import HTTPException

from app.main import (
    PromptRequest,
    app,
    grid,
    grid_clear,
    grid_stats,
    health_check,
    submit_prompt,
)


def test_health_check_returns_ok():
    assert health_check() == {"status": "ok"}


def test_prompt_roundtrip_uses_grid_cache_and_worker():
    prompt = f"day5 integration {uuid4()}"

    first_response = submit_prompt(PromptRequest(prompt=prompt))
    second_response = submit_prompt(PromptRequest(prompt=prompt))

    # Convert Pydantic models to dictionaries
    first_response = first_response.model_dump()
    second_response = second_response.model_dump()

    assert first_response["status"] == "completed"
    assert first_response["response"] == f"[stub] echo: {prompt}"
    assert first_response["cache"] == "miss"

    assert second_response["status"] == "completed"
    assert second_response["cache"] == "hit"
    assert second_response["response"] == first_response["response"]


def test_grid_stats_reports_configured_nodes():
    assert len(grid_stats()["nodes"]) == settings.node_count





def test_prompt_returns_failure_when_worker_fails(monkeypatch):
    import app.main as main

    def failing_process_prompt(request_id, prompt, inference_fn):
        return {
            "request_id": request_id,
            "status": "failed",
            "response": None,
            "error": "Failed to process prompt",
        }

    monkeypatch.setattr(main, "process_prompt", failing_process_prompt)

    with pytest.raises(HTTPException) as exc_info:
        main.submit_prompt(main.PromptRequest(prompt="failure test"))

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Failed to process prompt"



def test_grid_clear():
    prompt = f"clear grid integration {uuid4()}"

    assert submit_prompt(PromptRequest(prompt=prompt)).cache == "miss"
    assert submit_prompt(PromptRequest(prompt=prompt)).cache == "hit"

    route = next(
        route
        for route in app.routes
        if getattr(route, "path", None) == "/api/grid/clear"
    )
    assert route.status_code == 200
    assert grid_clear() == {"status": "cleared", "nodes": settings.node_count}

    stats = grid_stats()
    assert stats["cache_hits"] == 0
    assert stats["cache_misses"] == 0
    assert all(node["entries"] == 0 for node in stats["nodes"])
    assert all(len(node.policy) == 0 for node in grid.nodes)
