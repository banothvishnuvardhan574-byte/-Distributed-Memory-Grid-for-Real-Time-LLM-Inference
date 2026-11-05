# API Test Checklist

## Scope and execution

Exercise the root and health endpoints and the prompt endpoint with a valid,
empty, and missing prompt. Automated cases are in `tests/test_main.py`.

Run the checklist with:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_main.py -q
```

## Expected results and recorded actual results

| Test | Request | Expected status and response fields | Actual result | Status |
|---|---|---|---|---|
| Root | `GET /` | HTTP 200; JSON fields `message` (`LLM MemoryGrid API is running`) and `status` (`ready`) | HTTP 200; both fields and values matched | PASS |
| Health | `GET /health` | HTTP 200; JSON field `status` (`healthy`) | HTTP 200; `{"status":"healthy"}` | PASS |
| Valid prompt | `POST /api/prompt`, JSON `{"prompt":"  hello  "}` | HTTP 200; fields `request_id`, `status`, `prompt`, `response`, `cache`, `error`; trimmed prompt `hello`; completed status; non-empty request ID; response `[stub] echo: hello`; cache `hit` or `miss`; error `null` | HTTP 200; all expected fields present; prompt trimmed; completed status and stub response matched; request ID present; cache hit/miss; error `null` | PASS |
| Empty prompt | `POST /api/prompt`, JSON `{"prompt":"  "}` | HTTP 400; JSON field `detail` with `Prompt cannot be empty` | HTTP 400; `{"detail":"Prompt cannot be empty"}` | PASS |
| Missing prompt | `POST /api/prompt`, JSON `{}` | HTTP 422; validation error identifies `body.prompt` as missing | HTTP 422; validation detail identified `body.prompt` with type `missing` | PASS |

These are functional test results from the local FastAPI `TestClient`; they do
not represent a live-server or network test. The valid response is generated
by the application's stub inference implementation.

## Baseline timing approach for later performance testing

No baseline latency result is claimed by this checklist. For a comparable
future baseline:

1. Start the API with the same environment and configuration used for later
   comparison; record the commit, Python version, host, and configuration.
2. Measure client-observed duration around the complete HTTP request using a
   monotonic timer such as `time.perf_counter()`. Keep server middleware timing
   as a separate measurement if it is also collected.
3. Use a fixed prompt and request sequence. Record cache state for each
   request; report cold/cache-miss and warm/cache-hit measurements separately.
4. Run warm-ups separately, then collect a documented number of repetitions.
   Report sample count and a distribution (at least median and p95), not a
   single best-case duration.
5. Compare only runs made with the same measurement method and workload. Do
   not infer or claim a speedup until those measurements have been collected.

## Latest run

- Date: **2026-11-02**
- Command: `.\.venv\Scripts\python.exe -m pytest -q`
- Result: **94 passed**, 0 failed; 3 deprecation warnings from the existing
  Starlette/FastAPI test setup.
- The complete test inventory, frontend scripts, coverage classification,
  actual results, and API contract snapshot are recorded in
  [test_results.md](./test_results.md).
- TestClient results are in-process functional checks and do not represent a
  live-server/network end-to-end run. The acceptance test's one-run request
  timings are not a performance baseline.
