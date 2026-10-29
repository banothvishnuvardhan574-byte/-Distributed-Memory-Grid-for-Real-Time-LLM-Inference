# Distributed Memory Grid for Real-Time LLM Inference

LLM MemoryGrid is a FastAPI backend and React frontend for testing prompt
inference with a hash-routed, in-memory cache. The current backend uses a stub
inference function, making the project runnable without an external LLM
provider.

## Requirements

- Python 3.10 or newer
- Node.js and npm (for the frontend)

## Install and run the backend

From the repository root, create and activate a virtual environment, then
install the Python dependencies:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

On macOS or Linux, activate the environment with
`source .venv/bin/activate` instead.

Start the API:

```text
python -m uvicorn app.main:app --reload
```

The backend listens at <http://127.0.0.1:8000>. Interactive API documentation
is available at <http://127.0.0.1:8000/docs>.

## API endpoints

| Method | Endpoint | Description |
| --- | --- | --- |
| `GET` | `/` | API welcome message and readiness status. |
| `GET` | `/health` | Health check; returns `{"status":"ok"}`. |
| `POST` | `/api/prompt` | Submit JSON such as `{"prompt":"Hello"}`. Returns the response, request ID, and `hit`/`miss` cache result. Empty prompts return HTTP 400; worker failures return HTTP 500. |
| `GET` | `/api/grid/health` | Grid summary with node count, total cached entries, and per-node capacity. |
| `GET` | `/api/grid/stats` | Per-node cache details and aggregate `cache_hits`, `cache_misses`, and `hit_rate` (0.0 before any cache requests). |
| `POST` | `/api/grid/clear` | Clear all grid entries and reset cache metrics. |
| `POST` | `/api/pdf/today` | Upload a PDF as multipart field `file`. Optional multipart fields `day` and `month` choose a date; omitted fields default to today's corresponding date parts. Returns matching text and the effective target date. |

For example, a PDF request with an explicit date can be made with:

```bash
curl -X POST http://127.0.0.1:8000/api/pdf/today -F "file=@sample.pdf" -F "day=22" -F "month=oct"
```

The API accepts PDF filenames ending in `.pdf` and uses `pypdf` to extract
their text.

## Run the full stack

From the repository root, run both the backend and frontend with:

```bash
./run_dev.sh
```

The backend is available at `http://localhost:8000` and the frontend at
`http://localhost:5173`.

## Observability

- `GET /api/grid/health` reports node count, cached entries, and capacity per node.
- `GET /api/grid/stats` reports per-node statistics and the cache hit rate.
- Request method, path, status code, and elapsed time are logged for each API
  request in the Uvicorn console.

## Run the API demo

Start the backend, then open another terminal in the repository root and run:

```powershell
python scripts/demo.py
```

The demo checks API and grid health, grid configuration, cache clearing,
repeated-prompt caching, grid statistics, and empty-prompt validation.

## Run the tests

From the repository root:

Run the Day 17 integration checks:

```powershell
python -m pytest tests/test_day17_integration.py -v
```

Run the complete test suite:

```powershell
python -m pytest tests/ -v
```

## Run the frontend

In a second terminal:

```text
cd frontend
npm install
npm run dev
```

The Vite development server runs at <http://localhost:3000> and proxies API
requests to the backend at `http://localhost:8000`.
## Run the Full Stack

Start the backend and frontend using the project's development script:

```bash
./run_dev.sh