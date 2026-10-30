# Distributed Memory Grid for Real-Time LLM Inference

## Project overview
This project is a prototype for a distributed memory layer that can route and cache prompts for real-time LLM inference. The backend exposes FastAPI endpoints for request validation, health checks, and PDF-based date extraction utilities. The worker module is designed to process prompts in a separate process and report success, timeout, or failure states.

The architecture is organized around:

- FastAPI backend for API routes and validation
- Worker module for prompt processing with process-based timeout handling
- Frontend UI for interacting with the application
- Memory-grid concepts for routing and caching, still under active development

The project is currently in an early-to-mid development stage, with core API validation and worker behavior in place and the distributed routing milestone still to be completed.

---

## Prerequisites
Before running the project, make sure you have:

- Python 3.10 or newer
- Node.js 18+ and npm
- Git
- A terminal with PowerShell, bash, or zsh

For Windows, the commands below assume PowerShell.

---

## Virtual environment setup
From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

---

## Install dependencies
Backend dependencies:

```powershell
.\.venv\Scripts\python -m pip install -r requirements.txt
```

Frontend dependencies:

```powershell
cd frontend
npm install
cd ..
```

---

## Run the application
Start the backend:

```powershell
.\.venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Start the frontend:

```powershell
cd frontend
npm run dev
```

The frontend is usually served by Vite on a local dev port such as http://localhost:5173, while the FastAPI backend runs on http://localhost:8000.

---

## API endpoints
The backend currently exposes these routes:

### GET /
Returns a ready status payload.

```bash
curl http://localhost:8000/
```

Example response:

```json
{
  "message": "LLM MemoryGrid API is running",
  "status": "ready"
}
```

### GET /health
Checks service health.

```bash
curl http://localhost:8000/health
```

Example response:

```json
{
  "status": "healthy"
}
```

### POST /api/prompt
Accepts a prompt and validates that it is not empty.

Important: this endpoint currently acknowledges the request and returns a request ID; it does not run the real model inference pipeline yet. The actual LLM inference and worker integration are still pending until those components are implemented.

```bash
curl -X POST http://localhost:8000/api/prompt \
  -H "Content-Type: application/json" \
  -d '{"prompt": "Hello from the memory grid"}'
```

Example success response:

```json
{
  "request_id": "<uuid>",
  "status": "accepted",
  "prompt": "Hello from the memory grid",
  "message": "Prompt received successfully. LLM inference is not connected yet."
}
```

If the prompt is empty or whitespace-only, the API returns a 400 response with:

```json
{
  "detail": "Prompt cannot be empty"
}
```

### POST /api/pdf/today
Uploads a PDF and extracts date matches for a requested day/month.

```bash
curl -X POST http://localhost:8000/api/pdf/today \
  -F "file=@sample.pdf" \
  -F "day=11" \
  -F "month=oct"
```

---

## Test commands
Run the current API and integration validation set used by the project:

```powershell
.\.venv\Scripts\python -m pytest tests/test_main.py tests/test_day5_integration.py tests/test_day9_api.py -q
```

Run the full project suite if you want a broader smoke test:

```powershell
.\.venv\Scripts\python -m pytest -q
```

Current validation status:

- API route checks pass
- prompt validation checks pass
- cache hit/miss behavior passes
- worker timeout and failure handling pass under the current API contract
- warning: FastAPI/Starlette may show a deprecation warning related to httpx + TestClient in some environments

Note: the legacy `tests/test_worker.py` file contains older, mutually inconsistent failure assertions and is not used as the validation baseline for the current backend contract.

---

## Team roles
Suggested project roles for this repository:

- Project lead / architect: owns system design, roadmap, and integration decisions
- Backend engineer: maintains FastAPI routes, schemas, validation, and API contracts
- Worker / inference engineer: owns prompt processing, multiprocessing, retries, and timeout logic
- Frontend engineer: builds the UI and connects it to backend endpoints
- QA / validation engineer: writes regression and API tests, validates failure cases, and tracks quality gates
- DevOps / platform engineer: manages environment setup, dependency alignment, and deployment readiness

---

## Known limitations
This project is still a prototype, and some constraints should be expected:

- The `/api/prompt` endpoint currently only acknowledges input and returns a request ID; it does not yet execute real model inference
- Model inference and worker integration remain pending until the LLM pipeline is implemented
- Hash-based distributed routing is still incomplete according to the roadmap
- No persistent production-grade memory store is implemented yet
- The system is not yet production hardened for load balancing or multi-node deployment
- PDF extraction is limited to simple text extraction and date-matching checks
- Worker tests can be sensitive to Windows multiprocessing behavior and require the module to be importable in the active environment
- No formal benchmark or distributed performance baseline is in place yet

---

## Roadmap note
The roadmap documents the current milestone progress, and the most important remaining feature is the hash-based routing stage. Until that is implemented, the project should be treated as a working API prototype and early distributed-memory framework, not a complete production deployment.
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
| `GET` | `/api/grid/stats` | Per-node cache details and aggregate `cache_hits`, `cache_misses`, and `hit_rate` (0.0 before any cache requests). |
| `POST` | `/api/grid/clear` | Clear all grid entries and reset cache metrics. |
| `POST` | `/api/pdf/today` | Upload a PDF as multipart field `file`. Optional multipart fields `day` and `month` choose a date; omitted fields default to today's corresponding date parts. Returns matching text and the effective target date. |

For example, a PDF request with an explicit date can be made with:

```bash
curl -X POST http://127.0.0.1:8000/api/pdf/today -F "file=@sample.pdf" -F "day=22" -F "month=oct"
```

The API accepts PDF filenames ending in `.pdf` and uses `pypdf` to extract
their text.

## Run the tests

From the repository root:

```text
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
