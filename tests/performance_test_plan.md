# Reproducible Demonstration Benchmark

## What is measured

Run `scripts/performance_demo.py` from the repository root while the API is
running. It records two distinct measurements:

1. **API round-trip:** elapsed wall time from sending `POST /api/prompt` over
   HTTP until receiving its response. The endpoint is synchronous: a cache miss
   waits for the worker and inference. This is not a network-only measurement
   or an acknowledgement-only measurement.
2. **Model generation:** elapsed time calling the configured local inference
   adapter directly. Model load time and worker IPC are reported separately
   and excluded from this metric.

The adapter currently calls the model without streaming. **TTFT is not
applicable and must not be reported.**

## Environment and inputs

The script writes a JSON report containing OS, Python version, architecture,
CPU, physical memory (if available), installed package versions, current git
commit/branch, model-file presence/name, run timestamps, prompts, model limits,
and all per-sample outcomes. GPU is marked not queried rather than inferred.

The fixed prompt set is in `scripts/performance_demo.py`:

1. What is the capital of France?
2. Summarize in one sentence: AI is changing software development.
3. Write a short greeting for a new teammate.
4. List three benefits of distributed memory for LLM systems.
5. Explain caching in one paragraph.

Defaults are one warm-up per prompt and stage, three measured runs per prompt,
64 generated tokens, and a 20-second timeout. The report records overridden
values. API samples include unique suffixes so previous cache entries do not
turn the measured calls into cache-hit timings. Preserve the report alongside
the source commit if it is used for comparison.

## Setup and execution

Install the backend dependencies, start the backend in one terminal, and run
the benchmark from another:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
.\.venv\Scripts\python.exe scripts\performance_demo.py --runs 3 --warmup 1 --output results\demo-run.json
```

For genuine model generation, install `llama-cpp-python` and configure a local
GGUF model:

```powershell
$env:LLM_MODEL_PATH = "C:\models\your-instruct-model.gguf"
.\.venv\Scripts\python.exe scripts\performance_demo.py --runs 3 --warmup 1 --output results\demo-run.json
```

The project does not ship model weights or download a model automatically.
Without a valid model/runtime, generation is reported as blocked with the
adapter error. No mock/stub latency is labeled as model generation. API
connection errors and unsuccessful HTTP responses are retained as failed
samples instead of discarded.

## Report interpretation

For each measured stage, the JSON includes attempt/success/failure counts,
success rate, mean, median, nearest-rank p95, min/max, and individual records.
API latency summaries include failed attempts as well as successes; use the
per-sample status and HTTP code when interpreting the result. If no samples
were measurable, summary latencies remain `null`. Warm-up failures are listed
separately. The model load duration is informational and is not included in
generation latency.

Do not add API and generation latency together: API cache-miss timing already
contains worker and inference time, while direct generation is a separate
diagnostic measurement. A performance improvement claim requires a recorded
baseline and follow-up with the same prompts, model, hardware, runtime, warm-up,
and run count.
