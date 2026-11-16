import json

import httpx

import scripts.performance_demo as benchmark
from scripts.performance_demo import PROMPTS, summarize


def test_summarize_reports_successes_failures_and_nearest_rank_p95():
    samples = [
        {"status": "success", "latency_ms": 10.0},
        {"status": "failure", "latency_ms": 20.0},
        {"status": "success", "latency_ms": 30.0},
    ]

    assert summarize(samples) == {
        "attempts": 3,
        "successes": 2,
        "failures": 1,
        "success_rate_percent": 66.67,
        "latency_ms": {
            "mean": 20.0,
            "median": 20.0,
            "p95_nearest_rank": 30.0,
            "min": 10.0,
            "max": 30.0,
        },
    }


def test_summarize_empty_samples_has_no_invented_latency():
    assert summarize([]) == {
        "attempts": 0,
        "successes": 0,
        "failures": 0,
        "success_rate_percent": None,
        "latency_ms": {
            "mean": None,
            "median": None,
            "p95_nearest_rank": None,
            "min": None,
            "max": None,
        },
    }


def test_prompt_set_is_fixed_and_has_five_prompts():
    assert len(PROMPTS) == 5
    assert len(set(PROMPTS)) == len(PROMPTS)


def test_api_measurement_keeps_live_roundtrips_and_bypasses_cache(monkeypatch):
    seen_prompts = []
    real_client = httpx.Client

    def respond(request):
        body = json.loads(request.content)
        seen_prompts.append(body["prompt"])
        return httpx.Response(
            200,
            json={"request_id": str(len(seen_prompts)), "cache": "miss"},
        )

    def client_factory(**kwargs):
        return real_client(
            transport=httpx.MockTransport(respond),
            **kwargs,
        )

    monkeypatch.setattr(benchmark.httpx, "Client", client_factory)
    result = benchmark.measure_api(
        base_url="http://benchmark.test",
        runs=2,
        warmup=1,
        timeout=1,
    )

    assert result["status"] == "measured"
    assert result["summary"]["attempts"] == 10
    assert result["summary"]["successes"] == 10
    assert len(seen_prompts) == 15
    assert len(set(seen_prompts)) == len(seen_prompts)
    assert all(sample["cache"] == "miss" for sample in result["samples"])


def test_model_measurement_blocks_when_adapter_has_no_loaded_model(monkeypatch):
    class UnloadedAdapter:
        is_loaded = False

        def __init__(self, model_path=None):
            pass

    monkeypatch.setattr("inference.adapter.InferenceAdapter", UnloadedAdapter)

    result, _ = benchmark.measure_model(
        model_path=None,
        runs=1,
        warmup=0,
        max_new_tokens=8,
        timeout=1,
    )

    assert result["status"] == "blocked"
    assert result["samples"] == []
    assert result["summary"]["latency_ms"]["median"] is None
