# Day 11 - Backend Development and GitHub Contributions

**Project:** Distributed Memory Grid for Real-Time LLM Inference  
**Branch:** `member1-day11`

## Work completed

- Changed PDF date matching to default to the current date, while retaining
  explicit day/month parameters and lowercase month normalization.
- Added the aggregate cache `hit_rate` to `/api/grid/stats`, including a safe
  `0.0` result before any cache requests.
- Counted a cache miss only after successful inference and caching; failed
  worker requests return HTTP 500 and do not count as misses.
- Added coverage for default dates, explicit dates, cache hit/miss rates, and
  worker failures.
- Added the root setup/API README.

## Verification

- Baseline on the fetched Day 11 starting point: 56 tests passed, 2 existing
  FastAPI startup deprecation warnings.
- Focused Day 11 checks: 18 tests passed, 2 warnings.
- Full suite: 60 tests passed, 2 existing FastAPI startup deprecation warnings.
- Live API smoke checks passed for `/health`, prompt miss/hit, `/api/grid/stats`
  (1 hit, 1 miss, 0.5 hit rate), and PDF upload with today's date.
- Teammate PR review: no open pull requests were available when checked.
- Day 11 branch pushed. PR creation is pending GitHub sign-in in the integrated
  browser: <https://github.com/banothvishnuvardhan574-byte/-Distributed-Memory-Grid-for-Real-Time-LLM-Inference/compare/main...member1-day11>.

## Follow-up

- Replace the deprecated FastAPI startup event handler with a lifespan
  handler in a follow-up change.
- Open the PR against `main` from the compare link above and request review
  before merging.
