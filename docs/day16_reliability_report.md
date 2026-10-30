# Day 16 Reliability Test Report

## 1. Assignment

**Member 4 — Worker Reliability and Regression Testing**

Test timeout, failure, and repeated-request behaviour, and record the results.

## 2. Test Coverage

- **Timeout handling:** `test_process_prompt_handles_timeout`
- **Worker inference failure:** `test_process_prompt_handles_inference_error`
- **API worker failure:** `test_post_prompt_returns_500_when_worker_fails`
- **Repeated requests and caching:** `test_prompt_flow_after_health`
- **Health and observability:** `tests/test_day16_observability.py`

## 3. Issues Identified

The initial full test run on the updated shared code reported 17 failures and 73 passes.

The failures exposed problems including a duplicate `/api/prompt` route, an incorrectly implemented `/api/grid/config` endpoint, and outdated test expectations for prompt status and worker failure responses.

## 4. Fixes Applied

- Consolidated the duplicate `/api/prompt` handlers into one route.
- Ensured prompt processing is invoked once per request.
- Corrected `/api/grid/config` to return the configured grid settings.
- Updated test expectations to match the existing prompt and worker response contracts.

## 5. Validation Results

| Test run | Result |
|---|---|
| Initial full suite | 73 passed, 17 failed |
| Focused regression tests | 43 passed |
| Final full suite | 90 passed, 2 warnings |

Final command: `python -m pytest -q`

Final runtime: 14.38 seconds.

## 6. Warnings

Two FastAPI deprecation warnings remain related to startup event handling. They did not cause test failures and were not addressed in this assignment.

## 7. Current Status

The full test suite passes locally on `member4-day16`.

The backend changes should be reviewed by the Team Lead before merging into `main`.