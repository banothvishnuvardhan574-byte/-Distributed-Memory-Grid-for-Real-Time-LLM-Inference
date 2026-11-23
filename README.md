# Distributed Memory Grid for Real-Time LLM Inference

A prototype prompt-processing application with a FastAPI backend, a React/Vite
portal, and an in-memory cache distributed across memory nodes. Prompt inference
uses a local inference adapter; a compatible model/runtime must be configured
for generation to succeed.

## Features

- Prompt API with cache miss/hit responses and process-isolated worker handling.
- Coalescing for concurrent identical prompts so only one inference runs.
- Grid health and statistics, including per-node entries and cache hit rate.
- Stable hash-modulo routing, TTL expiration, and per-node LRU eviction.
- PDF upload for text extraction and date matching.
- React portal for prompt submission, PDF lookup, and live grid metrics.

## Quick start

Requirements: Python 3.10 or newer, Node.js 18 or newer, and npm.

Install backend dependencies and start the API from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

In another terminal, install frontend dependencies and start Vite:

```powershell
Set-Location frontend
npm install
npm run dev
```

The API is available at `http://localhost:8000`; interactive API documentation
is at `http://localhost:8000/docs`. Vite prints the frontend URL when it starts.
Alternatively, run `./run_dev.sh` from Git Bash or WSL to start both services.

 feat/recent-prompt-history-pagination
Prompt inference uses a local Ollama model. Install Ollama, then run:

```powershell
ollama pull qwen2.5:0.5b
```

The backend connects to Ollama at `http://127.0.0.1:11434` by default. Set
`OLLAMA_URL` and `OLLAMA_MODEL` to use a different local Ollama server or model.
Start Ollama before submitting prompts.
=======
### Optional local model

The inference adapter uses `llama-cpp-python` and a compatible GGUF model when
configured. These are not installed or downloaded by the default setup. Install
the runtime, obtain a model file separately, and set its path before starting
the API:

```powershell
.\.venv\Scripts\python.exe -m pip install llama-cpp-python
$env:LLM_MODEL_PATH = "C:\models\your-instruct-model.gguf"
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload
```

The model's license, source, and checksum should be verified before use. If no
usable model is configured, prompt generation fails explicitly; responses must
not be described as real model output.

## Architecture and measurement

`POST /api/prompt` validates a prompt, checks the in-memory grid, and on a cache
miss waits synchronously for the isolated worker to return. The worker calls
the inference adapter; successful text is cached. Therefore API round-trip
latency includes validation, cache/worker handling, and—on a miss—inference.
The demonstration benchmark measures that live HTTP round trip separately from
direct adapter generation time. The generation metric excludes model loading
and worker IPC. The adapter does not stream tokens, so TTFT is not measured.

For reproducible measurements, start the backend and run in a second terminal:

```powershell
.\.venv\Scripts\python.exe scripts\performance_demo.py --runs 3 --warmup 1 --output results\demo-run.json
```

The script uses a fixed set of five prompts, appends unique sample identifiers
to bypass cached answers for API requests, records hardware/software and git
metadata, and saves per-request results plus mean, median, nearest-rank p95,
min/max, and success/failure counts. It records unavailable model inference as
blocked and does not substitute a stub. A model file is optional for API
measurement; set `LLM_MODEL_PATH` or pass `--model-path` to measure genuine
generation. For options and the operator checklist, see
[the demo guide](docs/DEMO_GUIDE.md) and
[the performance test plan](tests/performance_test_plan.md).

## Known limitations

- The cache and worker are process-local; this prototype does not demonstrate
  multi-host distributed inference or durable/shared cache state.
- API round-trip measurements are end-to-end request times, not pure network
  overhead. Cache-miss requests include worker and generation time.
- Direct model-generation measurements exclude model load and worker IPC.
- The adapter makes non-streaming calls; TTFT is not applicable.
- The direct adapter timeout is checked after generation returns; it is not a
  hard interrupt. The API worker has its own process-level timeout.
- Results vary by host, runtime, model, and CPU/GPU configuration. Do not claim
  a speedup without a recorded comparable baseline.
 main

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | API readiness response. |
| `GET` | `/health` | Backend health check. |
| `POST` | `/api/prompt` | Submit a prompt; repeated prompts can return a cache hit. |
| `GET` | `/api/prompts/recent` | Read recent prompts, newest first; optional `status` (`completed` or `failed`), `limit` (1–50, default 50), and non-negative `offset`. `count` is the total number matching the status filter, before pagination. |
| `POST` | `/api/jobs` | Submit a prompt for asynchronous processing. |
| `GET` | `/api/jobs` | List jobs, newest first. Optional `status` (`running`, `completed`, or `failed`), `limit` (1–100), and non-negative `offset` for pagination. `count` is the total number matching the status filter, before pagination. |
| `DELETE` | `/api/jobs` | Remove finished jobs while preserving jobs still running. |
| `GET` | `/api/jobs/{job_id}` | Read the status and result of a submitted job. |
| `POST` | `/api/pdf/today` | Extract PDF text and find date-matching content. |
| `GET` | `/api/grid/config` | Read grid configuration. |
| `GET` | `/api/grid/health` | Read grid health and cached-entry totals. |
| `GET` | `/api/grid/stats` | Read cache totals, hit rate, and per-node statistics. |
| `POST` | `/api/grid/clear` | Clear cached entries and reset cache metrics. |

Use `/docs` for the live request and response schemas.

Concurrent requests for the same uncached prompt share one inference; each
request still receives its own request ID. The shared response is reported as a
cache hit for waiting requests.

The API endpoints are open locally and do not require an API key.

## Tests

Run the full backend suite from the repository root:

```powershell
python -m pytest tests/ -v
```

## Documentation

- [Project report](docs/PROJECT_REPORT.md) · [Final report PDF](docs/Internship_Report_Final.pdf)
- [Demo guide](docs/DEMO_GUIDE.md) · [v1.0 release notes](docs/RELEASE_v1.0.md)
- [Daily work sheets](docs/daily/)

## Status

**v1.0 complete — Day 20 final release.** Start the backend with
`uvicorn app.main:app --reload`, then start the frontend with `cd frontend` and
`npm run dev`. See the [demo guide](docs/DEMO_GUIDE.md) for the cache miss-to-hit
flow and PDF upload example.
 main
