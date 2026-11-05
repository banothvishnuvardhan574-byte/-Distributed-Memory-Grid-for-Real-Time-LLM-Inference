# Distributed Memory Grid for Real-Time LLM Inference

A prototype prompt-processing application with a FastAPI backend, a React/Vite
portal, and an in-memory cache distributed across memory nodes. Prompt inference
currently uses a deterministic stub rather than a production LLM provider.

## Features

- Prompt API with cache miss/hit responses and process-isolated worker handling.
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
| `POST` | `/api/prompts/batch` | Run up to 20 prompts and return each inference result. |
| `GET` | `/api/prompts/recent` | Read the latest 50 prompt results. |
| `POST` | `/api/jobs` | Submit a prompt for asynchronous inference. |
| `GET` | `/api/jobs/{job_id}` | Read an asynchronous job's status and result. |
| `POST` | `/api/pdf/today` | Extract PDF text and find date-matching content. |
| `GET` | `/api/pdf/search` | Search text from cached PDFs. |
| `GET` | `/api/metrics` | Read request counts, cache hits/misses, and job totals. |
| `GET` | `/api/grid/config` | Read grid configuration. |
| `GET` | `/api/grid/health` | Read grid health and cached-entry totals. |
| `GET` | `/api/grid/stats` | Read cache totals, hit rate, and per-node statistics. |
| `POST` | `/api/grid/clear` | Clear cached entries and reset cache metrics. |

Use `/docs` for the live request and response schemas.

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
