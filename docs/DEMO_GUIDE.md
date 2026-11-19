# Demo Guide

## Setup

Install the backend and frontend prerequisites from the repository root:

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
Set-Location frontend
npm install
Set-Location ..
```

Start the services:

```bash
./run_dev.sh
```

The script starts the FastAPI backend at `http://localhost:8000` and the Vite
frontend at `http://localhost:5173`. On Windows, run the script from Git Bash or
WSL. Or start them in separate terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
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

## Reproducible latency measurement

Keep the backend running. In another terminal, run:

```powershell
.\.venv\Scripts\python.exe scripts\performance_demo.py --runs 3 --warmup 1 --output results\demo-run.json
```

The report stores the five fixed prompts, one warm-up per prompt per stage,
three measured runs per prompt, timestamps, CPU/RAM, OS/Python/package/git
metadata, a source fingerprint, model configuration, and every request result. The API stage times
live HTTP requests to `POST /api/prompt` and uses unique prompt suffixes to
avoid cache hits. Its wall time includes the full synchronous handler and
worker (including generation on a miss), not only transport overhead. The
separate model stage times direct, non-streaming adapter generation after
model loading and warm-up. TTFT is not applicable because tokens are not
streamed. The direct adapter's timeout is checked after generation finishes;
it is not a hard interruption.

For actual model-generation numbers, install `llama-cpp-python`, set
`LLM_MODEL_PATH` to an existing compatible GGUF file (or pass `--model-path`),
then run the benchmark. The script records model absence/runtime errors as
blocked and leaves generation latency empty; it never substitutes mock output.
To change warm-up, repeat count, output path, or generation limit, use
`--help`. Keep the JSON report with the commit and environment when comparing
runs. Do not compare results across different model/runtime/hardware settings
as if they were a controlled speedup.

## Architecture and limitations

The API validates requests, checks the in-process memory grid, and calls the
isolated worker synchronously on cache misses. The worker invokes the adapter;
successful responses are cached. `POST /api/jobs` is the separate asynchronous
job-submission API. The cache and worker are local to one process/host and do
not establish cross-host distribution. Prompt response behavior requires a
configured model; no model is bundled. API RTT is not pure network latency,
and direct generation time excludes model loading and worker IPC.

## Demo checklist

- [ ] Record the commit and machine/software metadata in the benchmark JSON.
- [ ] Confirm `/health` is healthy and API prompt submissions succeed.
- [ ] Show a prompt cache miss, then a repeated prompt cache hit.
- [ ] Show grid counters and node entry counts.
- [ ] Upload a PDF and show the matching date result.
- [ ] Run the benchmark with fixed prompts, warm-up, and repeat count.
- [ ] Report API RTT and model generation separately; do not report TTFT.
- [ ] If model/runtime setup is unavailable, state model generation is blocked.
- [ ] Capture frontend and backend test outcomes, including warnings/failures.
- [ ] Mark browser prompt/cache and PDF workflows not run unless they were
      manually exercised; automated in-process API tests are not browser E2E.

## Fallback

- If the frontend fails, use the `curl.exe` commands above and open
  `http://localhost:8000/docs` for the Swagger UI.
- If `./run_dev.sh` is unavailable, start backend and frontend separately using
  the setup commands.
- If no local model is configured, prompt inference returns an explicit worker
  error; do not present it as a successful stub or a live LLM response.

## Screenshot checklist

- Full frontend dashboard with backend connection status and grid metrics.
- Prompt response showing the initial cache miss and the repeated cache hit.
- PDF date lookup result showing the target date and matches.
- `/api/grid/stats` JSON with per-node entries and cache counters.
- Benchmark JSON showing measured and blocked stages without fabricated data.
- Latest full-suite output and final pass/fail/blocked/not-run counts.
