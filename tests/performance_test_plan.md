# Performance Test Plan

## Goal
Measure the latency and reliability of the app in a repeatable way using a small fixed prompt set. The plan separates:

1. API acknowledgement latency: time for the web API to accept and validate a prompt
2. Real model generation latency: time spent generating a model response after the request has been accepted

This matters because the current FastAPI route at `/api/prompt` acknowledges the request immediately and does not actually run model generation yet. The worker process is the correct place to measure actual generation time once the model is connected.

---

## Fixed prompt set
Use the same small prompt list every run. Example:

- "What is the capital of France?"
- "Summarize this in one sentence: AI is changing software development."
- "Write a short greeting for a new teammate."
- "List 3 benefits of distributed memory for LLM systems."
- "Explain caching in one paragraph."

Use 5 prompts so the test is stable but still covers multiple lengths.

---

## Repeat count
Run each prompt a fixed number of times, for example:

- 20 runs per prompt
- total = 100 requests

This gives enough data for median and p95 while keeping the test short and repeatable.

---

## Timing definitions

### 1) API acknowledgement latency
Measure from request send time to HTTP response receipt for the API endpoint.

- Endpoint: `POST /api/prompt`
- Success condition: HTTP 200 and a valid `request_id`
- Failure condition: HTTP 400/422 or network error
- Metric: round-trip latency in milliseconds

Pseudo:

```python
start = time.perf_counter()
response = client.post("/api/prompt", json={"prompt": prompt})
ack_latency_ms = (time.perf_counter() - start) * 1000
```

### 2) Real model generation latency
Measure the actual worker execution time once the prompt has already been accepted.

- Function: `worker.worker.process_prompt(...)`
- Start timer before calling `process_prompt`
- Stop timer when the worker returns a final result
- Success condition: `status == "completed"`
- Failure condition: `status == "failed"` or timeout
- Metric: worker processing latency in milliseconds

Pseudo:

```python
start = time.perf_counter()
result = process_prompt(request_id, prompt, inference_fn)
model_latency_ms = (time.perf_counter() - start) * 1000
```

Important: do not combine acknowledgement latency and model-generation latency into one value. They are separate stages.

---

## Success/failure recording
For every request, record:

- timestamp_utc
- prompt_id or prompt_index
- prompt_text
- request_id
- stage (`api_ack` or `model_generation`)
- status (`success` or `failure`)
- http_status_code (for API only)
- latency_ms
- error_message (if any)

Example row:

```text
timestamp_utc,prompt_id,prompt_text,request_id,stage,status,latency_ms,http_status_code,error_message
2026-10-18T10:00:00Z,1,"What is the capital of France?",abc123,api_ack,success,32.4,200,
```

---

## Environment record
Capture one environment block per test run:

- date/time (UTC)
- OS
- Python version
- architecture
- CPU model
- memory available
- project commit/branch
- app mode (`local`, `dev`, `prod`)
- model type/model name (if connected)
- worker timeout setting
- prompt retry count

Example:

```text
run_id=perf-2026-10-18-01
platform=Windows-11
python=3.12.7
cpu=Intel(R) Core(TM) i7-12700H
ram=16 GB
fastapi=0.x.x
worker_timeout_seconds=5.0
```

---

## Run procedure
1. Freeze the prompt list
2. Record the environment block
3. For prompt in prompts:
   - run it `N` times
   - call API endpoint each time and record `api_ack` latency and result
   - if model path is enabled, call the worker and record `model_generation` latency and result
4. Save results to CSV/JSON
5. Compute summary statistics:
   - mean
   - median
   - p95
   - min/max
   - success rate
   - failure count

---

## Summary metrics to report
- API ack latency: mean, median, p95
- Model generation latency: mean, median, p95
- API success rate
- Model success rate
- Timeout count
- Error count by type
- Environment snapshot for each run

---

## Suggested command to run
From the project root:

```bash
python -m pytest tests/test_performance_api.py -q
```

Or, if the project uses a dedicated benchmark script:

```bash
python tests/performance_benchmark.py --runs 20 --prompts prompts.txt --output results/performance.csv
```

---

## Notes for this repo
At the moment, the API route `/api/prompt` is an acknowledgement endpoint, not a full generation endpoint. For a true performance test, use two measurements:

- API acknowledgement latency through `/api/prompt`
- model latency through the worker function `process_prompt(...)` when connected to the actual LLM or a deterministic stub

This separation keeps the numbers honest and avoids treating the acknowledgement step as if it were real model generation time.
