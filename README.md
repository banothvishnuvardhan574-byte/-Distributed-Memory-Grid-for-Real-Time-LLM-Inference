# Distributed Memory Grid for Real-Time LLM Inference

A prototype prompt-processing service with a FastAPI backend, a React/Vite
portal, and an in-memory grid that caches prompt results across memory nodes.
Inference currently uses a deterministic stub rather than a production LLM.

## Features

- Prompt API with cache miss/hit responses and a process-isolated worker.
- Memory-grid health and statistics, including per-node entries and hit rate.
- Stable hash-based routing, TTL expiration, and per-node LRU eviction.
- PDF upload for text extraction and date matching.
- React portal for prompt submission, PDF lookup, and live grid metrics.

## Quick start

Requirements: Python, Node.js, and npm.

Start the backend from the repository root:

```powershell
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

In another terminal, start the frontend:

```powershell
Set-Location frontend
npm install
npm run dev
```

The API is available at `http://localhost:8000`, its interactive docs are at
`http://localhost:8000/docs`, and Vite prints the frontend URL when it starts.
You can also use `./run_dev.sh` from Git Bash or WSL to start both services.

## API

| Method | Endpoint | Purpose |
| --- | --- | --- |
| `GET` | `/health` | Backend health check. |
| `POST` | `/api/prompt` | Submit a prompt; a repeated prompt can return a cache hit. |
| `POST` | `/api/pdf/today` | Extract PDF text and find date-matching content. |
| `GET` | `/api/grid/config` | Read grid configuration. |
| `GET` | `/api/grid/health` | Read grid health and cached-entry totals. |
| `GET` | `/api/grid/stats` | Read cache totals, hit rate, and per-node statistics. |
| `POST` | `/api/grid/clear` | Clear cached entries and reset cache metrics. |

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

**v1.0 complete — Day 20 final release.** Run the backend with
`uvicorn app.main:app --reload`, then run the frontend with
`cd frontend` and `npm run dev`. See the [demo guide](docs/DEMO_GUIDE.md) for
the full miss-to-hit flow and PDF upload example.
