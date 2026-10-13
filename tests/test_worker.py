
import time
import pytest

from worker.worker import process_prompt



def test_process_prompt_returns_response():
    result = process_prompt(
        request_id="123",
        prompt="Hello",
        inference_fn=lambda prompt: "Hello back!",
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
        inference_fn=lambda prompt: f"You said: {prompt}",
    )

    assert result["response"] == "You said: Hello"


def test_process_prompt_rejects_empty_prompt():
    with pytest.raises(ValueError):
        process_prompt(
            request_id="789",
            prompt="   ",
            inference_fn=lambda prompt: "This should not run",
        )

def test_process_prompt_handles_inference_error():
    def failing_inference(prompt: str) -> str:
        raise RuntimeError("Model is unavailable")

    result = process_prompt(
        request_id="999",
        prompt="Hello",
        inference_fn=failing_inference,
    )

    assert result["status"] == "failed"
    assert result["request_id"] == "999"
    assert result["response"] == "Failed to process prompt"

def test_process_prompt_handles_timeout():
    def slow_inference(prompt: str) -> str:
        time.sleep(2)
        return "This response is too late"

    result = process_prompt(
        request_id="timeout-001",
        prompt="Hello",
        inference_fn=slow_inference,
        timeout_seconds=0.1,
    )

    assert result["request_id"] == "timeout-001"
    assert result["status"] == "failed"
    assert result["response"] == "Inference timed out"
