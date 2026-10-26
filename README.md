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

## Start the full stack

Install the frontend dependencies once:

```bash
npm --prefix frontend install
```

With the Python virtual environment active, run this from the repository root
in Git Bash or WSL:

```bash
bash run_dev.sh
```

The script starts the API on port `8000` and the Vite frontend on port `5173`.
Press `Ctrl+C` to stop both development servers.

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

The Vite development server runs at <http://localhost:5173> and proxies API
requests to the backend at `http://localhost:8000`.
