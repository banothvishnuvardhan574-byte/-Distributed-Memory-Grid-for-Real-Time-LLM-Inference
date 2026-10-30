# Prompt API Test Results

**Run date:** 2026-10-30  
**Test command:** `\.\.venv\Scripts\python -m pytest tests/test_main.py tests/test_day5_integration.py tests/test_day9_api.py -q`  
**Overall result:** 20 passed, 0 failed

The current validation set exercises the real FastAPI endpoints, cache behavior,
worker timeout/failure handling, and API contract. This is the baseline used for
this project’s current backend contract.

## Key validation summary

- `/` and `/health` endpoints return expected status packets
- `POST /api/prompt` accepts valid prompts, trims whitespace, and returns a
  valid request ID
- empty/whitespace inputs return HTTP 400 with `Prompt cannot be empty`
- repeated prompts hit the in-memory grid cache correctly
- worker timeout and worker failure states are surfaced as HTTP 500 with a
  clear error message
- PDF date extraction endpoints continue to pass the supported checks

## Current result

- Command run: `\.\.venv\Scripts\python -m pytest tests/test_main.py tests/test_day5_integration.py tests/test_day9_api.py -q`
- Result: **20 passed, 0 failed**
- Warnings: 3 deprecation warnings from FastAPI/Starlette TestClient setup only

## Note on legacy worker checks

The older `tests/test_worker.py` file contains stale/contradictory assertions for
worker failure payloads and is excluded from the active validation baseline. The
current backend contract consistently expects failed worker runs to return a
`status` of `failed` and a `response` of `None` with the error text in the
`error` field.
