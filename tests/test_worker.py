
import time

import pytest

from worker.worker import process_prompt


def successful_inference(prompt: str) -> str:
    return "Hello back!"


def echo_inference(prompt: str) -> str:
    return f"You said: {prompt}"


def failing_inference(prompt: str) -> str:
    raise RuntimeError("Model is unavailable")


def slow_inference(prompt: str) -> str:
    time.sleep(2)
    return "This response is too late"


def test_process_prompt_returns_response():
    result = process_prompt(
        request_id="123",
        prompt="Hello",
        inference_fn=successful_inference,
    )

    assert result == {
        "request_id": "123",
        "status": "completed",
        "response": "Hello back!",
    }


def test_process_prompt_removes_extra_spaces():
    result = process_prompt(
        request_id="456",
        prompt="  Hello  ",
        inference_fn=echo_inference,
    )

    assert result["response"] == "You said: Hello"
    assert result["status"] == "completed"


def test_process_prompt_rejects_empty_prompt():
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        process_prompt(
            request_id="789",
            prompt="   ",
            inference_fn=successful_inference,
        )


def test_process_prompt_handles_inference_error():
    result = process_prompt(
        request_id="999",
        prompt="Hello",
        inference_fn=failing_inference,
    )

    assert result["request_id"] == "999"
    assert result["status"] == "failed"
    assert result["response"] == "Failed to process prompt"


def test_process_prompt_handles_timeout():
    result = process_prompt(
        request_id="timeout-001",
        prompt="Hello",
        inference_fn=slow_inference,
        timeout_seconds=0.1,
    )

    assert result["request_id"] == "timeout-001"
    assert result["status"] == "failed"
    assert result["response"] == "Inference timed out"


def test_process_prompt_rejects_invalid_timeout():
    with pytest.raises(ValueError, match="Timeout must be greater than zero"):
        process_prompt(
            request_id="timeout-002",
            prompt="Hello",
            inference_fn=successful_inference,
            timeout_seconds=0,
        )
