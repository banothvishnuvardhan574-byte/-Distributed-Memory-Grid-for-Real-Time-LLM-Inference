# Prompt API Test Results

**Run date:** 2026-10-28  
**Test command:** `.\.venv\Scripts\python.exe -m pytest tests/test_main.py -q -s`  
**Overall result:** 5 passed, 0 failed

The acceptance test sends requests through FastAPI's `TestClient` to the actual
`POST /api/prompt` route. Successful cache misses run the worker in a child
process using the application's current stub inference function.

| Test name | Input | Expected result | Actual result | Status code | Pass/fail | Measured request time |
|---|---|---|---|---:|---|---:|
| Normal prompt | `Explain what a cache is.` | HTTP 200; completed response from stub; cache miss | HTTP 200; response `[stub] echo: Explain what a cache is.`; cache miss | 200 | PASS | 2905.48 ms |
| Repeat normal prompt | `Explain what a cache is.` (same input as normal prompt) | HTTP 200; same response served from cache; cache hit | HTTP 200; same response as first request; cache hit | 200 | PASS | 11.91 ms |
| Empty prompt | Empty string | HTTP 400; `Prompt cannot be empty` | HTTP 400; `Prompt cannot be empty` | 400 | PASS | 16.67 ms |
| Whitespace-only prompt | Three spaces, a tab, then two spaces | HTTP 400; `Prompt cannot be empty` | HTTP 400; `Prompt cannot be empty` | 400 | PASS | 17.67 ms |
| Special-character prompt | `Special chars: !@#$%^&*()_+-=[]{};':",./<>?` | HTTP 200; completed response; cache miss | HTTP 200; response `[stub] echo: Special chars: !@#$%^&*()_+-=[]{};':",./<>?`; cache miss | 200 | PASS | 3026.46 ms |
| Separate prompt A | `Describe a blue ocean.` | HTTP 200; completed response; cache miss | HTTP 200; response `[stub] echo: Describe a blue ocean.`; cache miss | 200 | PASS | 2344.20 ms |
| Separate prompt B | `Describe a quiet forest.` | HTTP 200; completed response; cache miss, separate from prompt A | HTTP 200; response `[stub] echo: Describe a quiet forest.`; cache miss | 200 | PASS | 2072.47 ms |

## Cache and latency findings

- The repeated prompt produced a cache hit on the second request. The grid
  statistics after the test showed **1 hit**, **4 misses**, and a **0.2 hit
  rate**. The empty and whitespace-only requests were rejected before cache
  lookup and did not affect those counts.
- This verifies hits in the application's in-memory `MemoryGrid` during one
  process run. It does not establish persistence across restarts or sharing
  between separately running application processes.
- Latency is measured, not simulated: the request middleware records elapsed
  wall-clock time for its log entry. The API response does not return latency.
  The table's timings were independently measured around each `TestClient`
  request using `time.perf_counter()`.
- These are single-run local test-client timings, not a production or network
  benchmark. Cache-miss timings include worker child-process startup; the
  inference is a stub echo, not a real LLM. No speedup claim is made from these
  measurements.

The run reported three deprecation warnings from the existing FastAPI/Starlette
test setup; they did not cause test failures.
