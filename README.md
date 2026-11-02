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

* Python 3.10 or newer
* Node.js and npm
* Git

## Backend Setup

Run these commands from the repository root in PowerShell:

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
```

If PowerShell prevents environment activation, check your execution policy or activate the environment using an appropriate alternative.

### Start the Backend

```powershell
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

The API is available at:

* API base: http://127.0.0.1:8000
* Interactive API documentation: http://127.0.0.1:8000/docs

## API Endpoints

| Method | Endpoint           | Description                                                               |
| ------ | ------------------ | ------------------------------------------------------------------------- |
| GET    | `/`                | Returns the API welcome message and readiness status.                     |
| GET    | `/health`          | Checks API health.                                                        |
| POST   | `/api/prompt`      | Submits a prompt and returns its response, request ID, and cache result.  |
| GET    | `/api/grid/health` | Returns grid health information, including node count and cached entries. |
| GET    | `/api/grid/stats`  | Returns per-node statistics and aggregate cache metrics.                  |
| POST   | `/api/grid/clear`  | Clears cached entries and resets cache metrics.                           |
| POST   | `/api/pdf/today`   | Accepts a PDF upload and performs date-based text matching.               |

### Submit a Prompt

Example request:

```json
{
  "prompt": "Hello"
}
```

The prompt endpoint returns the generated or cached response and indicates whether the request was a cache hit or miss.

According to the current API contract, empty prompts return HTTP 400 and worker failures return HTTP 500.

### Upload a PDF

The PDF endpoint accepts a multipart upload using the field `file`. Optional `day` and `month` fields specify the target date.

Example using curl:

```bash
curl -X POST http://127.0.0.1:8000/api/pdf/today \
  -F "file=@sample.pdf" \
  -F "day=22" \
  -F "month=oct"
```

The backend uses `pypdf` to extract PDF text. Confirm the accepted filename and validation rules in the current implementation.

## Observability

The grid statistics endpoint provides cache-related information, including:

* Cache hits
* Cache misses
* Cache hit rate
* Per-node statistics

Request logging records the HTTP method, path, response status, and elapsed time in the Uvicorn console.

## Run the API Demo

Start the backend first. Open a second terminal in the repository root, activate the virtual environment, and run:

```powershell
python scripts/demo.py
```

The demo is intended to check API health, grid configuration, cache clearing, repeated-prompt caching, grid statistics, and empty-prompt validation.

## Run the Tests

Run the Day 17 integration tests:

```powershell
python -m pytest tests/test_day17_integration.py -v
```

Run the complete test suite:

```powershell
python -m pytest tests/ -v
```

Resolve any dependency or test-collection errors before treating the test suite as passing.

## Frontend Setup

Open another terminal:

```powershell
cd frontend
npm install
npm run dev
```

Use the local URL printed by Vite in the terminal. The frontend's port and API proxy target depend on the current Vite configuration.

## Run the Full Stack

The repository includes a `run_dev.sh` script for starting the development environment:

```bash
./run_dev.sh
```

This command requires a compatible shell, such as Git Bash or WSL on Windows. Alternatively, run the backend and frontend in separate terminals using the commands above.

## Project Status

The backend currently uses a stub inference function rather than requiring an external LLM provider. This makes it possible to develop and test the caching, routing, API, and frontend workflows independently of a production inference service.
