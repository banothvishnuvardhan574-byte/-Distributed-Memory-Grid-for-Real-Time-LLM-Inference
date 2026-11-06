import time

import pytest

worker_module = pytest.importorskip(
    "worker.worker",
    reason="worker module not available",
)

process_prompt = worker_module.process_prompt

from inference.exceptions import (
    InferenceError,
    InferenceTimeoutError,
    InvalidPromptError,
    ModelNotReadyError,
)


def successful_inference(prompt: str) -> str:
    return "Hello back!"


def echo_inference(prompt: str) -> str:
    return f"You said: {prompt}"


def failing_inference(prompt: str) -> str:
    raise RuntimeError("Model is unavailable")


def slow_inference(prompt: str) -> str:
    time.sleep(2)
    return "This response is too late"


def invalid_prompt_inference(prompt: str) -> str:
    raise InvalidPromptError("Invalid test prompt")


def model_not_ready_inference(prompt: str) -> str:
    raise ModelNotReadyError("Model is unavailable")


def timeout_inference(prompt: str) -> str:
    raise InferenceTimeoutError("Inference exceeded timeout")


def inference_error(prompt: str) -> str:
    raise InferenceError("Internal inference error")


@pytest.fixture(autouse=True)
def cleanup_worker():
    """Ensure each test releases its worker process."""
    yield
    worker_module.shutdown_worker()


def test_worker_module_success_when_available():
    result = process_prompt(
        request_id="123",
        prompt="Hello",
        inference_fn=successful_inference,
        timeout_seconds=20,
    )

    assert result["request_id"] == "123"
    assert result["status"] == "completed"
    assert result["response"] == "Hello back!"
    assert result["error"] is None
    assert isinstance(result["latency_ms"], int)
    assert result["latency_ms"] >= 0


def test_worker_module_failure_when_available():
    result = process_prompt(
        request_id="999",
        prompt="Hello",
        inference_fn=failing_inference,
        timeout_seconds=20,
    )

    assert result["request_id"] == "999"
    assert result["status"] == "failed"
    assert result["response"] is None
    assert result["error"] == "Failed to process prompt"
    assert isinstance(result["latency_ms"], int)


def test_process_prompt_removes_extra_spaces():
    result = process_prompt(
        request_id="456",
        prompt="  Hello  ",
        inference_fn=echo_inference,
        timeout_seconds=20,
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
        timeout_seconds=20,
    )

    assert result["request_id"] == "999"
    assert result["status"] == "failed"
    assert result["response"] is None
    assert result["error"] == "Failed to process prompt"
    assert isinstance(result["latency_ms"], int)


def test_process_prompt_handles_timeout():
    result = process_prompt(
        request_id="timeout-001",
        prompt="Hello",
        inference_fn=slow_inference,
        timeout_seconds=0.1,
    )

    assert result["request_id"] == "timeout-001"
    assert result["status"] == "failed"
    assert result["response"] is None
    assert result["error"] == "Inference timed out"
    assert isinstance(result["latency_ms"], int)

    # A timed-out worker must be removed.
    assert worker_module._worker_process is None


def test_process_prompt_rejects_invalid_timeout():
    with pytest.raises(ValueError, match="Timeout must be greater than zero"):
        process_prompt(
            request_id="timeout-002",
            prompt="Hello",
            inference_fn=successful_inference,
            timeout_seconds=0,
        )


def test_worker_process_is_reused_between_requests():
    first_result = process_prompt(
        request_id="persistent-001",
        prompt="First request",
        inference_fn=echo_inference,
        timeout_seconds=20,
    )

    first_process_id = worker_module._worker_process.pid

    second_result = process_prompt(
        request_id="persistent-002",
        prompt="Second request",
        inference_fn=echo_inference,
        timeout_seconds=20,
    )

    second_process_id = worker_module._worker_process.pid

    assert first_result["status"] == "completed"
    assert second_result["status"] == "completed"
    assert first_result["request_id"] == "persistent-001"
    assert second_result["request_id"] == "persistent-002"
    assert first_process_id == second_process_id


def test_worker_restarts_after_timeout():
    timeout_result = process_prompt(
        request_id="restart-001",
        prompt="Slow request",
        inference_fn=slow_inference,
        timeout_seconds=0.1,
    )

    assert timeout_result["status"] == "failed"
    assert timeout_result["error"] == "Inference timed out"
    assert worker_module._worker_process is None

    retry_result = process_prompt(
        request_id="restart-002",
        prompt="Retry request",
        inference_fn=successful_inference,
        timeout_seconds=20,
    )

    assert retry_result["request_id"] == "restart-002"
    assert retry_result["status"] == "completed"
    assert retry_result["response"] == "Hello back!"


@pytest.mark.parametrize(
    ("inference_fn", "expected_error"),
    [
        (invalid_prompt_inference, "InvalidPrompt:"),
        (model_not_ready_inference, "ModelUnavailable:"),
        (timeout_inference, "Inference timed out"),
        (inference_error, "InferenceError:"),
    ],
)
def test_worker_preserves_typed_inference_errors(
    inference_fn,
    expected_error,
):
    result = process_prompt(
        request_id="typed-error-001",
        prompt="Test prompt",
        inference_fn=inference_fn,
        timeout_seconds=20,
    )

    assert result["status"] == "failed"
    assert result["response"] is None
    assert result["error"].startswith(expected_error)
    assert isinstance(result["latency_ms"], int)