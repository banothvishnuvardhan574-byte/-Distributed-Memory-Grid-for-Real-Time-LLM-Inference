 suraj-inference
# LLM MemoryGrid — Model & Inference Integration

**Component Owner:** Suraj Kotrange  
**Assigned Branch:** `suraj-inference`  
**Execution Window:** 2–14 November 2026  
**Primary Hand-off:** `generate_response(prompt: str) -> str` interface for `nikhila-worker` and `vishnu-backend`.

---

## 1. Overview & Objective

This component provides a lightweight, robust, reproducible local inference pipeline for the LLM MemoryGrid demonstrator. In accordance with the project rules:
* Model execution is isolated behind a single public interface: `generate_response(prompt: str) -> str`.
* The adapter enforces single-instance model loading in memory (no reloading weights per prompt).
* Generation parameters are strictly bounded (max tokens, timeout, and explicit error states).
* Stub/echo outputs are never disguised as real generation.

---

## 2. Hardware Constraints Summary

From empirical host benchmarking on 3 Nov 2026:
* **CPU:** 2 vCPUs (Intel Xeon 6985P-C)
* **RAM:** 7.8 GiB total (~6.7 GiB free)
* **GPU:** None (CPU inference only)
* **Storage:** 18 GiB free disk

**Recommended Model:** `Qwen2.5-0.5B-Instruct` (GGUF Q4_K_M, ~380 MB download, ~650 MB RAM working set).

Full feasibility study available in: [`docs/INFERENCE_OPTIONS.md`](docs/INFERENCE_OPTIONS.md).

---

## 3. Project Structure

```
├── .gitignore
├── docs/
│   └── INFERENCE_OPTIONS.md          # Hardware audit, model benchmarks & Vishnu proposal
├── inference/
│   ├── __init__.py                   # Package exports
│   ├── adapter.py                    # InferenceAdapter class & generate_response contract
│   └── exceptions.py                 # Custom error hierarchy (ModelNotReadyError, etc.)
├── examples/
│   └── worker_integration_example.py # Minimal callable example for Nikhila
└── tests/
    └── test_inference.py             # Unit & contract tests for Sagar's test runner
```

---

## 4. Quick Start & Setup

### Environment Setup
```bash
# Recommended Python version: 3.11+
python3 -m venv .venv
source .venv/bin/activate

# Install runtime dependencies
pip install llama-cpp-python
```

### Running Unit Tests
```bash
python3 -m unittest discover tests
```

### Worker Integration Pattern
```python
from inference import generate_response, ModelNotReadyError, InferenceTimeoutError

try:
    response_text = generate_response("Explain distributed inference", max_tokens=128)
    print("Response:", response_text)
except ModelNotReadyError as e:
    print("Model not loaded:", e)
except InferenceTimeoutError as e:
    print("Timeout:", e)
```

# Distributed Memory Grid for Real-Time LLM Inference

A prototype prompt-processing application with a FastAPI backend, a React/Vite
portal, and an in-memory cache distributed across memory nodes. Prompt inference
currently uses a deterministic stub rather than a production LLM provider.

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
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
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

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/` | API readiness response. |
| `GET` | `/health` | Backend health check. |
| `POST` | `/api/prompt` | Submit a prompt; repeated prompts can return a cache hit. |
| `POST` | `/api/jobs` | Submit a prompt for asynchronous processing (requires `X-API-Key`). |
| `GET` | `/api/jobs` | List jobs, newest first; optional `status`, `limit` (1–100), and non-negative `offset` for pagination. |
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

`POST /api/prompt` and `POST /api/jobs` require an `X-API-Key` header and allow
30 requests per key per 60 seconds per API process. Configure accepted keys as
a comma-separated `API_KEYS` value in the backend environment (for example, in
`.env`):

```dotenv
API_KEYS=replace-with-a-long-random-key
```

Enter an accepted key in the prompt form. Do not commit API keys to source
control. The in-memory rate limit is process-local and resets when the API
restarts.

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
