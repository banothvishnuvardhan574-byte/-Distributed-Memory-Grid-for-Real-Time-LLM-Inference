# Distributed Memory Grid for Real-Time LLM Inference

**LLM MemoryGrid** is a FastAPI backend and React frontend for testing prompt inference with a hash-routed, in-memory cache. The current backend uses a stub inference function, allowing the project to run without an external LLM provider.

## Features

* FastAPI backend for prompt submission and processing.
* Hash-based routing across in-memory cache nodes.
* Prompt caching with hit/miss tracking.
* Grid health and cache statistics endpoints.
* PDF text extraction and date-based matching.
* Request logging and API observability.
* React frontend built with Vite.
* Automated tests and an API demonstration script.

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
