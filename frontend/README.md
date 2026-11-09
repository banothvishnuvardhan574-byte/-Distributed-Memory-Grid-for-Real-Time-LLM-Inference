# MemoryGrid frontend

## Run locally

Start the backend from the repository root in one terminal:

```powershell
.\.venv\Scripts\Activate.ps1
python -m uvicorn app.main:app --reload
```

In a second terminal, install dependencies and start Vite from the `frontend`
directory:

```powershell
cd frontend
npm ci
npm run dev
```

Open <http://localhost:5173>. Vite proxies `/health` and `/api` requests to
`http://localhost:8000` by default, so no frontend environment file is needed
for the local setup.

To call a different backend directly, set `VITE_API_URL` in
`frontend/.env.local`, for example:

```text
VITE_API_URL=http://localhost:8000
```

Restart Vite after changing the environment file. For a different frontend
origin, configure the backend's `CORS_ORIGINS` setting to allow that origin.

## Demo workflows

- **Prompt:** Enter a prompt and submit it. The response panel shows the worker
  response, request status, latency, request ID, and cache result. Repeating a
  prompt within the cache lifetime should report a cache hit.
- **PDF lookup:** In the PDF lookup section, choose a PDF and optionally specify
  a day and month, then select **Find date**. The result shows the target date,
  match count, and matching sentences, or a no-matches message. Upload or
  processing failures are shown in the UI.

The backend currently uses a stub inference function, so prompt responses are
for demonstrating API, cache, and UI behavior rather than production inference.

## Frontend checks

Run these commands from `frontend`:

```powershell
npm run build
npm run lint
```
