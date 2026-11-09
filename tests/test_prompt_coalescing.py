from concurrent.futures import Future, ThreadPoolExecutor
import threading

import app.main as main


def test_concurrent_identical_prompts_share_inference(monkeypatch):
    inference_started = threading.Event()
    follower_waiting = threading.Event()
    release_inference = threading.Event()
    calls = []

    class ObservedFuture(Future):
        def result(self, timeout=None):
            follower_waiting.set()
            return super().result(timeout)

    def fake_process_prompt(request_id, prompt, inference_fn):
        calls.append(request_id)
        inference_started.set()
        assert release_inference.wait(timeout=2)
        return {
            "request_id": request_id,
            "status": "completed",
            "response": "shared response",
            "error": None,
        }

    monkeypatch.setattr(main, "Future", ObservedFuture)
    monkeypatch.setattr(main, "process_prompt", fake_process_prompt)
    main.grid_clear()

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            leader = executor.submit(
                main.run_prompt,
                "same prompt",
                "leader-request",
            )
            assert inference_started.wait(timeout=2)
            follower = executor.submit(
                main.run_prompt,
                "same prompt",
                "follower-request",
            )
            assert follower_waiting.wait(timeout=2)
            release_inference.set()

            leader_result = leader.result(timeout=2)
            follower_result = follower.result(timeout=2)

        assert calls == ["leader-request"]
        assert leader_result["request_id"] == "leader-request"
        assert follower_result["request_id"] == "follower-request"
        assert leader_result["cache"] == "miss"
        assert follower_result["cache"] == "hit"
        assert follower_result["response"] == leader_result["response"]

        stats = main.grid_stats()
        assert stats["cache_misses"] == 1
        assert stats["cache_hits"] == 1
    finally:
        release_inference.set()
        main.grid_clear()


def test_inference_exception_reaches_waiters_and_allows_retry(monkeypatch):
    inference_started = threading.Event()
    follower_waiting = threading.Event()
    release_inference = threading.Event()
    calls = []

    class ObservedFuture(Future):
        def result(self, timeout=None):
            follower_waiting.set()
            return super().result(timeout)

    def fake_process_prompt(request_id, prompt, inference_fn):
        calls.append(request_id)
        if len(calls) == 1:
            inference_started.set()
            assert release_inference.wait(timeout=2)
            raise RuntimeError("inference failed")
        return {
            "request_id": request_id,
            "status": "completed",
            "response": "retry succeeded",
            "error": None,
        }

    monkeypatch.setattr(main, "Future", ObservedFuture)
    monkeypatch.setattr(main, "process_prompt", fake_process_prompt)
    main.grid_clear()

    try:
        with ThreadPoolExecutor(max_workers=2) as executor:
            leader = executor.submit(
                main.run_prompt,
                "retry prompt",
                "first-request",
            )
            assert inference_started.wait(timeout=2)
            follower = executor.submit(
                main.run_prompt,
                "retry prompt",
                "waiting-request",
            )
            assert follower_waiting.wait(timeout=2)
            release_inference.set()

            for result in (leader, follower):
                try:
                    result.result(timeout=2)
                except RuntimeError as exc:
                    assert str(exc) == "inference failed"
                else:
                    raise AssertionError(
                        "Expected the inference error to propagate"
                    )

        result = main.run_prompt("retry prompt", "retry-request")

        assert calls == ["first-request", "retry-request"]
        assert result["status"] == "completed"
        assert result["cache"] == "miss"
    finally:
        release_inference.set()
        main.grid_clear()
