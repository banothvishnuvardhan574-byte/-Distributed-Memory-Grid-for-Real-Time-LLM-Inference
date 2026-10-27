# Day 10 - Daily Work Sheet

**Project:** Distributed Memory Grid for Real-Time LLM Inference

**Phase:** Week 2 - Implementation

**Team Lead:** Member 1

## Today's Goal

Code review round 1 and the integration checkpoint: verify every module working
together on `main`, run the full application and test suite, and fix the first
real bugs found during review.

## Member 1 - Team Lead Tasks

### Morning: review round 1

- Pull or confirm the latest `main`, install the requirements, start the API,
  and run the entire test suite:

  ```text
  git checkout main
  git pull
  pip install -r requirements.txt
  uvicorn app.main:app --reload
  pytest tests/ -v
  ```

- Check the endpoints in Swagger UI at <http://localhost:8000/docs>:
  `/health`, `/api/prompt` (first a miss, then a hit), `/api/pdf/today` with a
  real PDF, and `/api/grid/stats`.
- Review integration issues and fix the bugs found during the review.
- Write the Week 2 midpoint status note for the report and maintain a list of
  bugs/follow-up work for Days 11-12.

### Add `POST /api/grid/clear`

- Clear the entries and LRU bookkeeping for every memory node.
- Reset cache hit and miss counters to zero.
- Return a successful response with the cleared status and node count.
- Add an integration test that fills the cache, clears it, and verifies both
  the endpoint result and zeroed cache statistics.

## Team Tasks

| Member | Day 10 task | Expected output |
| --- | --- | --- |
| Member 2 | Add `GridRouter` tests: the same key always selects the same node, and 100 keys distribute roughly evenly across nodes. | Routing is stable and distribution tests pass. |
| Member 3 | Handle multi-page PDFs and large files (10+ pages); measure extraction time. | No crash, all matches returned, and timing recorded. |
| Member 4 | Add an integration test for `POST /api/prompt` through the worker and assert the `request_id` roundtrip (`tests/test_api_worker.py`). | API-to-worker integration test passes. |
| Member 5 | Complete the PDF upload UI: file picker, `POST /api/pdf/today`, and display of the `matches` list. | Browser upload roundtrip works and displays matches. |

## Team Test Commands

```text
pytest tests/ -v
curl -X POST http://localhost:8000/api/grid/clear
curl -X POST http://localhost:8000/api/pdf/today -F "file=@sample.pdf"
```

Use a real PDF in place of `sample.pdf` when checking the upload endpoint.

## GitHub Steps (Everyone)

```text
git checkout -b member<N>-day10
git add .
git commit -m "day10: <what you did>"
git push origin member<N>-day10
```

Open a PR for review. Member 1 reviews each PR and merges it after checks pass.
After all PRs are merged:

```text
git checkout main
git pull
git tag day10
git push origin day10
```

## End-of-Day Checklist

- [ ] Full roundtrip works: UI to prompt to cache hit; UI to PDF to matches.
- [ ] `/api/grid/clear` is added and its test passes.
- [ ] All tests are green (`pytest` and any frontend checks).
- [ ] Bug list for Days 11-12 is created.
- [ ] All PRs are merged and the `day10` tag is pushed.
- [ ] Member status notes are collected.

## Expected Output for Report

Capture screenshots of the full green pytest run, `/api/grid/stats` before and
after clearing, and the browser showing both prompt and PDF upload workflows.
