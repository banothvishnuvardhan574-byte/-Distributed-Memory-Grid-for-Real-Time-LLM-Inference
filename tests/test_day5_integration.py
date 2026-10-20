
from uuid import uuid4

from app.core.config import settings
from app.main import PromptRequest, grid_stats, health_check, submit_prompt


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

