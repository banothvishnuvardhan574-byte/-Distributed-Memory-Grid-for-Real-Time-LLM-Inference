# Test and Evidence Matrix

**Run date:** 2026-11-02

**Python command:** `.\.venv\Scripts\python.exe -m pytest -q`

**Python result:** 94 passed, 0 failed; 3 deprecation warnings

**Frontend commands:** `npm run lint` and `npm run build` (run from `frontend\`)

This matrix records existing tests and the latest observed results. Test IDs
are pytest node IDs so each entry maps directly to a collected test. Python
actuals are from the complete suite run above; all assertions passed. The
frontend has lint/build scripts but no automated test script.
Within a table cell, abbreviated `::test_...` IDs use the file path in the
first full node ID in that cell.

## Current API contract

The status codes and JSON examples below match the current implementation and
automated tests. They document observed behavior; this file does not record
stakeholder approval or a separate contract sign-off.

| Request | Expected status | Expected JSON |
|---|---:|---|
| `GET /` | 200 | `{"message":"LLM MemoryGrid API is running","status":"ready"}` |
| `GET /health` | 200 | `{"status":"healthy"}` |
| `POST /api/prompt` with `{"prompt":"  hello  "}` | 200 | `{"request_id":"<UUID>","status":"completed","prompt":"hello","response":"[stub] echo: hello","cache":"miss" or "hit","error":null}` |
| `POST /api/prompt` with empty/whitespace prompt | 400 | `{"detail":"Prompt cannot be empty"}` |
| `POST /api/prompt` with missing `prompt` or more than 4000 characters | 422 | FastAPI validation JSON with `detail`; missing input identifies `["body","prompt"]` and type `missing` |
| `POST /api/prompt` when worker fails | 500 | `{"detail":"<safe worker error>"}`; the tested message is `"Failed to process prompt"` |
| `POST /api/pdf/today` with an unsupported extension or unreadable/empty PDF | 400 | JSON `detail`; unsupported extension is `"Please upload a PDF file."`, unreadable content begins `"Unable to read PDF content"` |

Worker-internal success/failure packets are also tested: success uses
`{"request_id":"req-123","status":"completed","response":"...","error":null}`;
failure uses
`{"request_id":"req-123","status":"failed","response":null,"error":"..."}`.
The worker's packet is not the API's HTTP error response.

## Unit tests

| Test ID / collected cases | Component; setup and input | Expected output | Actual output | Command | Result / date |
|---|---|---|---|---|---|
| `tests/test_eviction.py::test_no_eviction_under_capacity`<br>`::test_evicts_oldest_key`<br>`::test_touch_refreshes_key`<br>`::test_remove_forgets_key`<br>`::test_invalid_capacity_raises`<br>`::test_negative_capacity_raises` | LRU eviction policy; insert, touch, remove keys and try invalid capacities. | No eviction under capacity; least-recently-used key evicted; refresh/removal respected; invalid capacities raise `ValueError`. | All six assertions passed with the expected keys/errors. | Python command above | PASS — 2026-11-02 |
| `tests/test_hashing.py::test_hash_prompt_is_stable`<br>`::test_hash_prompt_normalizes_whitespace`<br>`::test_hash_prompt_differs_for_different_prompts`<br>`::test_hash_to_int_returns_int` | Prompt hashing; repeat, whitespace-variant, distinct prompts, and integer conversion. | Stable hashes; whitespace normalization; different prompts differ; integer result. | All four assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_memory_grid.py::test_grid_routes_set_and_get_to_the_same_node`<br>`::test_grid_stats_reports_all_nodes`<br>`::test_grid_rejects_invalid_node_count`<br>`::test_grid_evicts_lru_key_on_target_node` | In-memory grid; route keys across nodes, inspect stats, invalid node count, and exceed one-node capacity. | Read-after-write; correct node stats; invalid count rejected; oldest key evicted on target node. | All four assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_memory_node.py::test_set_and_get`<br>`::test_missing_key_returns_none`<br>`::test_expired_key_returns_none`<br>`::test_evicts_lru_when_over_capacity`<br>`::test_lru_eviction_stays_within_capacity_under_load`<br>`::test_expiration_at_ttl_boundary_removes_key_and_lru_entry`<br>`::test_delete`<br>`::test_stats`<br>`::test_invalid_capacity`<br>`::test_negative_capacity`<br>`::test_negative_ttl` | Memory node; set/get/delete, missing and expired keys, LRU pressure, stats, and invalid capacity/TTL. | Values and counters match operations; expiration and LRU remove entries; invalid capacity/TTL raise `ValueError`. | All eleven assertions passed, including 1,000 insertions bounded to capacity. | Python command above | PASS — 2026-11-02 |
| `tests/test_router.py::test_route_is_deterministic`<br>`::test_route_within_node_range`<br>`::test_routes_distributed_across_nodes`<br>`::test_route_many`<br>`::test_empty_key_raises`<br>`::test_invalid_node_count_raises[0]`<br>`::test_invalid_node_count_raises[-1]` | Grid router; same/different keys, batches, empty key, and zero/negative node counts. | Deterministic in-range routing, distribution across nodes, correct batch mapping; invalid inputs raise `ValueError`. | All seven assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_pdf_extraction.py::test_extract_text_from_first_pdf`<br>`::test_extract_text_from_second_pdf`<br>`::test_corrupt_pdf_raises_http_exception`<br>`::test_extract_text_from_valid_pdf_without_text_returns_empty_string` | PDF text extractor; generated PDFs with text, malformed bytes, and blank page. | Extract embedded text; malformed PDF raises HTTP 400; valid textless PDF returns empty string. | All four assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_pdf_workflow.py::test_find_today_date_matches_detects_today_entries`<br>`::test_find_today_date_matches_common_month_name_and_numeric_formats`<br>`::test_find_today_date_matches_handles_empty_text`<br>`::test_normalize_pdf_text_collapses_extraction_whitespace`<br>`::test_find_today_date_matches_defaults_to_current_date`<br>`::test_find_today_date_matches_normalizes_month_input` | PDF date matching/normalization; fixed dates, month variants, numeric formats, and empty text. | Return only matching sentences; normalize whitespace/months; empty input returns no matches; default date is current date. | All six assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_worker.py::test_worker_module_success_when_available`<br>`::test_worker_module_failure_when_available`<br>`::test_process_prompt_removes_extra_spaces`<br>`::test_process_prompt_rejects_empty_prompt`<br>`::test_process_prompt_handles_inference_error`<br>`::test_process_prompt_handles_timeout`<br>`::test_process_prompt_rejects_invalid_timeout` | Worker isolated with deterministic fake inference; success, exception, timeout, normalization, and invalid inputs. | Successful/failed worker packet matches the schema above; blank prompt and invalid timeout raise `ValueError`; timeout reports `"Inference timed out"`. | All seven assertions passed, including timeout handling. | Python command above | PASS — 2026-11-02 |

## Mocked and in-process integration tests

These tests exercise app handlers or FastAPI `TestClient`. Worker/inference
failures are monkeypatched where noted; other successful prompt paths use the
local stub inference, not a live LLM service.

| Test ID / collected cases | Component; setup and input | Expected output | Actual output | Command | Result / date |
|---|---|---|---|---|---|
| `tests/test_api_worker.py::test_post_prompt_roundtrips_request_id_through_worker`<br>`::test_post_prompt_returns_500_when_worker_fails` | Prompt API and worker; fixed request ID/stub for success, monkeypatched worker failure. | Success preserves ID and response fields; failure returns HTTP 500 with JSON `detail`. | Both API response assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_day11_prompt_api.py::test_prompt_endpoint_rejects_missing_prompt`<br>`::test_prompt_endpoint_rejects_blank_prompt`<br>`::test_prompt_endpoint_returns_expected_response_fields` | Prompt API via `TestClient`; missing/blank input and mocked request ID/inference. | Missing input 422; blank 400; valid response has the six contract fields and expected values. | All three assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_day12_config.py::test_memory_grid_applies_capacity_to_every_node`<br>`::test_application_grid_uses_configured_capacity`<br>`::test_grid_config_endpoint_returns_active_settings` | Grid configuration; construct a two-node grid and GET `/api/grid/config`. | Capacity applied to each node; endpoint returns configured node count, capacity, and TTL. | All three assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_day12_pdf_validation.py::test_upload_rejects_unsupported_file_extension`<br>`::test_upload_rejects_empty_filename` | PDF handler invoked with text/empty filenames and upload bytes. | HTTP 400 with `{"detail":"Please upload a PDF file."}`. | Both assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_day13_pdf_api.py::test_post_pdf_today_upload_returns_expected_date_matches` | PDF API via `TestClient`; generated real PDF containing a fixed matching date. | HTTP 200; filename, target date, one matching sentence, and completion message. | Response matched all expected fields. | Python command above | PASS — 2026-11-02 |
| `tests/test_day13_validation.py::test_empty_prompt_returns_400`<br>`::test_oversized_prompt_returns_422`<br>`::test_valid_prompt_returns_200` | Prompt API via `TestClient`; empty, 4001-character, and valid prompts. | HTTP 400, 422, and 200 respectively; valid response completed and has cache state. | All three assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_day16_integration.py::test_grid_health_endpoint`<br>`::test_prompt_flow_after_health` | Grid health and prompt API via `TestClient`; clear grid, submit the same prompt twice. | Healthy grid; first prompt misses and second hits cache. | Both assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_day16_observability.py::test_grid_health_reports_expected_fields` | Grid health API via `TestClient`. | HTTP 200 with healthy status, node count, cached-entry count, and capacity. | All expected fields present and valid. | Python command above | PASS — 2026-11-02 |
| `tests/test_day17_integration.py::test_app_imports_and_home`<br>`::test_health_endpoint`<br>`::test_all_grid_endpoints`<br>`::test_prompt_end_to_end`<br>`::test_validation_and_worker_error_paths`<br>`::test_pdf_rejects_non_pdf`<br>`::test_prompt_returns_500_when_worker_fails` | Multiple API routes via in-process `TestClient`; clear/cache prompt, invalid inputs, PDF rejection, mocked worker failure. | Home/health/grid routes return expected status and fields; cache miss then hit; validation and worker/PDF failures return expected error codes. | All seven cases passed. This `TestClient` case named `end_to_end` is not a live-server E2E test. | Python command above | PASS — 2026-11-02 |
| `tests/test_day5_integration.py::test_health_check_returns_ok`<br>`::test_prompt_roundtrip_uses_grid_cache_and_worker`<br>`::test_grid_stats_reports_configured_nodes`<br>`::test_grid_stats_reports_cache_hits_misses_and_hit_rate`<br>`::test_prompt_returns_failure_when_worker_fails`<br>`::test_grid_clear`<br>`::test_prompt_reprocesses_after_cached_response_expires` | Direct app handlers and grid; prompt roundtrip/cache stats, mocked worker failure, clear, and mocked clock/worker for TTL expiry. | Correct health helper value, cache miss/hit counters, HTTP 500 on failure, clear resets grid, expiry reprocesses prompt. | All seven assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_day9_api.py::test_prompt_response_model_is_published_in_openapi`<br>`::test_empty_prompt_returns_bad_request`<br>`::test_worker_failure_returns_http_500_with_detail`<br>`::test_worker_failure_returns_http_500_without_counting_a_cache_miss`<br>`::test_pdf_endpoint_defaults_to_current_date`<br>`::test_empty_pdf_is_rejected_safely`<br>`::test_invalid_pdf_is_rejected_safely` | Direct app handlers/OpenAPI; mock worker and date, plus empty/invalid PDF bytes. | OpenAPI references `PromptResponse`; prompt failures are 400/500; failed work does not increment misses; PDF date defaults and invalid files return 400. | All seven assertions passed. | Python command above | PASS — 2026-11-02 |
| `tests/test_main.py::test_home_returns_ready_status`<br>`::test_health_check_returns_healthy_status`<br>`::test_submit_prompt_trims_prompt_and_returns_request_id`<br>`::test_submit_prompt_rejects_empty_prompt`<br>`::test_submit_prompt_rejects_missing_prompt`<br>`::test_prompt_acceptance_inputs_and_cache_behavior` | Main routes via `TestClient`; home/health, valid/missing/empty prompts, repeats, whitespace, special characters, and distinct prompts. | Contract JSON and codes match snapshot; UUID request ID; trim prompt; cache hit/miss and stats match requests. | All six tests passed. Acceptance case covered seven inputs; expected cache stats were 1 hit, 4 misses, hit rate 0.2. | Python command above | PASS — 2026-11-02 |
| `tests/test_pdf_grid_handoff.py::test_pdf_text_is_normalized_and_stored_in_grid` | PDF handler with mocked extracted text and generated upload; inspect normalized grid entry. | One date match; normalized extracted text stored under the PDF cache key. | Assertions passed. | Python command above | PASS — 2026-11-02 |

## Genuine end-to-end coverage

| Test ID | Component; setup and input | Expected output | Actual output | Command | Result / date |
|---|---|---|---|---|---|
| `E2E-NONE` | No test starts the backend as a separate live service and calls it over the network, and no test connects to a real LLM provider. | Add a separately identified live-service test before claiming genuine end-to-end coverage. | No genuine end-to-end test exists in the collected suite; `TestClient` tests are in-process. | `.\.venv\Scripts\python.exe -m pytest --collect-only -q` | NOT RUN — 2026-11-02 |

## Frontend validation scripts

| Test ID | Component; setup and input | Expected output | Actual output | Command | Result / date |
|---|---|---|---|---|---|
| `FE-LINT` | Frontend lint; run package script in `frontend\`. | Oxlint exits successfully. | Exit 0; one `react(set-state-in-effect)` warning at `src/App.jsx:180`. | `npm run lint` (in `frontend\`) | PASS with warning — 2026-11-02 |
| `FE-BUILD` | Frontend production build; run package script in `frontend\`. | Vite creates production assets. | Build succeeded; 10,995 modules transformed. | `npm run build` (in `frontend\`) | PASS — 2026-11-02 |

`frontend\package.json` defines `dev`, `build`, `lint`, and `preview`; it does
not define a frontend test script. No browser-based UI tests were present or
run.

## Run notes

- Full pytest collection found 94 test cases; `pytest -q` completed with
  **94 passed, 0 failed**.
- Pytest emitted three pre-existing deprecation warnings involving Starlette's
  `TestClient`/httpx and FastAPI `on_event` startup handling.
- This is a local validation record dated 2026-11-02, not a CI or production
  deployment run.

## Live local smoke verification

**Run date:** 2026-11-11

The backend and Vite frontend were started locally on `127.0.0.1:8000` and
`127.0.0.1:5173`. These checks crossed the live HTTP API and worker, but the
configured inference function is still `stub_inference`; this is not a real
LLM-adapter verification.

| Scenario | Actual result |
|---|---|
| `GET /health` | HTTP 200; `healthy`. |
| Three unique `POST /api/prompt` requests | All HTTP 200, `completed`, with distinct request IDs and non-empty output. Responses were `[stub] echo: ...`; cache was `miss` for each. Request IDs: `60418558-406e-4345-b99b-caf41eed1984`, `64e6bbef-9295-4270-9b4c-cd0302a291f0`, `8b1caa13-e861-4788-bef0-91496ac1f5d6`. |
| Repeat the first prompt | HTTP 200, `completed`, same cached output, new request ID `f1834952-3e9b-416f-bb70-cd4ac40fedf8`, cache `hit`. |
| `GET /api/grid/stats` after those four requests | Actual in-memory backend reported 1 cache hit, 3 misses, 25% hit rate; three entries distributed across four live nodes. |
| Browser prompt workflow | Loaded the frontend; submitted a prompt and saw completed status, output, request ID `80f2d2ce-7f1a-4e23-b8c4-c42976cd7b05`, latency (77 ms), and cache miss. Re-submitted the same prompt and saw cache hit with a new request ID. |
| Frontend lint/build | `npm run lint` exited 0 with one `react(set-state-in-effect)` warning at `src/App.jsx:180`; `npm run build` succeeded (10,995 modules). |
| Focused API/worker/cache tests | 22 passed, 0 failed; three deprecation warnings. Command: `.\.venv\Scripts\python.exe -m pytest tests\test_api_worker.py tests\test_day11_prompt_api.py tests\test_day16_integration.py tests\test_day17_integration.py tests\test_worker.py -q`. |

This smoke check did not exercise a PDF upload in the browser or a real
inference provider. Genuine inference remains blocked until the adapter is
wired/configured and its model service is available.
