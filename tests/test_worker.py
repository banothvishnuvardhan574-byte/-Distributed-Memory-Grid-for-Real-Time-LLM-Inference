
import threading
from types import SimpleNamespace

import pytest

worker_module = pytest.importorskip("worker.worker", reason="worker module not available")
process_prompt = worker_module.process_prompt


def mocked_successful_inference(prompt: str) -> str:
    return "Hello back!"


def mocked_echo_inference(prompt: str) -> str:
    return f"You said: {prompt}"


def mocked_failing_inference(prompt: str) -> str:
    raise RuntimeError("Model is unavailable")


def test_mocked_worker_success():
    result = process_prompt(
        request_id="123",
        prompt="Hello",
        inference_fn=mocked_successful_inference,
        timeout_seconds=20,
    )

    assert result == {
        "request_id": "123",
        "status": "completed",
        "response": "Hello back!",
        "error": None,
    }


def test_mocked_worker_failure():
    result = process_prompt(
        request_id="999",
        prompt="Hello",
        inference_fn=mocked_failing_inference,
        timeout_seconds=20,
    )

    assert result["status"] == "failed"
    assert result["request_id"] == "999"
    assert result["response"] is None
    assert result["error"] == "Failed to process prompt"


def test_mocked_process_prompt_removes_extra_spaces():
    result = process_prompt(
        request_id="456",
        prompt="  Hello  ",
        inference_fn=mocked_echo_inference,
        timeout_seconds=20,
    )

    assert result["response"] == "You said: Hello"
    assert result["status"] == "completed"


def test_process_prompt_rejects_empty_prompt():
    with pytest.raises(ValueError, match="Prompt cannot be empty"):
        process_prompt(
            request_id="789",
            prompt="   ",
            inference_fn=mocked_successful_inference,
        )


def test_mocked_process_prompt_handles_inference_error():
    result = process_prompt(
        request_id="999",
        prompt="Hello",
        inference_fn=mocked_failing_inference,
        timeout_seconds=20,
    )

    assert result == {
        "request_id": "999",
        "status": "failed",
        "response": None,
        "error": "Failed to process prompt",
    }


def test_mocked_process_prompt_handles_timeout_and_cleans_up(monkeypatch):
    inference_started = threading.Event()
    release_inference = threading.Event()
    inference_finished = threading.Event()
    threads = []
    real_thread = threading.Thread

    class TrackedThread(real_thread):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            threads.append(self)

    def blocked_inference(prompt: str) -> str:
        inference_started.set()
        try:
            release_inference.wait()
            return "This response is too late"
        finally:
            inference_finished.set()

    monkeypatch.setattr(
        worker_module,
        "threading",
        SimpleNamespace(Event=threading.Event, Thread=TrackedThread),
    )

    try:
        result = process_prompt(
            request_id="timeout-001",
            prompt="Hello",
            inference_fn=blocked_inference,
            timeout_seconds=0.1,
        )

        assert result == {
            "request_id": "timeout-001",
            "status": "failed",
            "response": None,
            "error": "Inference timed out",
        }
        assert inference_started.wait(timeout=1)
    finally:
        release_inference.set()

    assert inference_finished.wait(timeout=1)
    assert len(threads) == 1
    threads[0].join(timeout=1)
    assert not threads[0].is_alive()


def test_process_prompt_rejects_invalid_timeout():
    with pytest.raises(ValueError, match="Timeout must be greater than zero"):
        process_prompt(
            request_id="timeout-002",
            prompt="Hello",
            inference_fn=mocked_successful_inference,
            timeout_seconds=0,
        )
