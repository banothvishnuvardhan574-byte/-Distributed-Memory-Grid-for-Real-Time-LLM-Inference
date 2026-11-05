# Demo Guide (Day 20)

## Setup

From the repository root, run:

```bash
./run_dev.sh
```

The script starts the FastAPI backend at `http://localhost:8000` and the Vite
frontend at `http://localhost:5173`. On Windows, run the script from Git Bash or
WSL. Alternatively, start the services in separate terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --port 8000
```

```powershell
Set-Location frontend
npm run dev
```

## Demo flow

1. Check backend health:

   ```bash
   curl.exe http://localhost:8000/health
   ```

   Expect `{"status":"healthy"}`.

2. Submit a prompt and confirm the cache miss:

   ```powershell
   curl.exe -X POST http://localhost:8000/api/prompt -H "Content-Type: application/json" -d '{"prompt":"Explain what a memory grid does."}'
   ```

   The response should include `"cache":"miss"`.

3. Submit the same prompt again. The response should include
   `"cache":"hit"`—the memory-grid proof.

4. Inspect hit/miss totals, hit rate, and per-node entry counts:

   ```bash
   curl.exe http://localhost:8000/api/grid/stats
   ```

5. Inspect node count and total cached entries:

   ```bash
   curl.exe http://localhost:8000/api/grid/health
   ```

6. Upload a PDF for date matching. Leave `day` and `month` out to use today's
   date, or provide both fields for a repeatable example:

   ```powershell
   curl.exe -X POST http://localhost:8000/api/pdf/today -F "file=@schedule.pdf;type=application/pdf" -F "day=11" -F "month=October"
   ```

   The response includes the target date, match count, and matching text. A
   small text-based PDF containing `Meeting on 11 October 2026.` makes a useful
   deterministic example.

7. Open `http://localhost:5173`. Submit a prompt in the portal, upload the same
   PDF in the date lookup panel below the dashboard, and show the live grid
   metrics (hits, misses, hit rate, and per-node entries). Metrics refresh every
   two seconds. Repeating the prompt should change its result from miss to hit.

## Fallback

- If the frontend fails, use the `curl.exe` commands above and open
  `http://localhost:8000/docs` for the Swagger UI.
- If `./run_dev.sh` is unavailable, start backend and frontend separately using
  the setup commands.
- The backend currently uses stub inference; responses are deterministic
  echoes, not results from a production LLM.

## Screenshot checklist

- Full frontend dashboard with backend connection status and grid metrics.
- Prompt response showing the initial cache miss and the repeated cache hit.
- PDF date lookup result showing the target date and matches.
- `/api/grid/stats` JSON with per-node entries and cache counters.
- Green full-suite output from `pytest tests/ -v`.
