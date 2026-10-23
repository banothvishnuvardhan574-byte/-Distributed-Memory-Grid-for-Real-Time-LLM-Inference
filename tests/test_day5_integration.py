
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


def test_grid_stats_reports_cache_hits_misses_and_hit_rate():
    grid_clear()
    prompt = f"cache metrics integration {uuid4()}"

    initial_stats = grid_stats()
    assert initial_stats["cache_hits"] == 0
    assert initial_stats["cache_misses"] == 0
    assert initial_stats["hit_rate"] == 0.0

    assert submit_prompt(PromptRequest(prompt=prompt)).cache == "miss"
    miss_stats = grid_stats()
    assert miss_stats["cache_hits"] == 0
    assert miss_stats["cache_misses"] == 1
    assert miss_stats["hit_rate"] == 0.0

    assert submit_prompt(PromptRequest(prompt=prompt)).cache == "hit"
    hit_stats = grid_stats()
    assert hit_stats["cache_hits"] == 1
    assert hit_stats["cache_misses"] == 1
    assert hit_stats["hit_rate"] == 0.5

    grid_clear()




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


    
def test_prompt_reprocesses_after_cached_response_expires(monkeypatch):
    import app.main as main
    import app.grid.memory_node as memory_node

    now = [100.0]
    monkeypatch.setattr(memory_node.time, "time", lambda: now[0])

    calls = []

    def fake_process_prompt(request_id, prompt, inference_fn):
        calls.append(prompt)
        return {
            "request_id": request_id,
            "status": "completed",
            "response": f"response-{len(calls)}",
            "error": None,
        }

    monkeypatch.setattr(main, "process_prompt", fake_process_prompt)
    monkeypatch.setattr(main.settings, "default_ttl_seconds", 5)

    main.grid_clear()
    prompt = f"ttl regression {uuid4()}"

    first = main.run_prompt(prompt, "request-1")
    second = main.run_prompt(prompt, "request-2")

    assert first["cache"] == "miss"
    assert second["cache"] == "hit"
    assert second["response"] == first["response"]
    assert len(calls) == 1

    now[0] = 105.0

    third = main.run_prompt(prompt, "request-3")

    assert third["cache"] == "miss"
    assert third["response"] == "response-2"
    assert len(calls) == 2

