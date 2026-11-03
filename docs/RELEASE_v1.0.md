# v1.0 - Final Release (Day 21)

The Distributed Memory Grid for Real-Time LLM Inference is complete and ready
for the final demo.

## Delivered

- **FastAPI backend:** prompt submission and cache handling at `/api/prompt`,
  asynchronous prompt jobs at `/api/jobs`, PDF date lookup at `/api/pdf/today`,
  cached PDF text search at `/api/pdf/search`, and grid configuration, health,
  statistics, and cache-clear endpoints under `/api/grid`.
- **MemoryGrid:** deterministic hash-based routing across memory nodes,
  configurable TTL expiration, per-node LRU eviction, and hit/miss and hit-rate
  metrics.
- **Worker:** process-isolated prompt processing with timeout and failure
  handling. Inference is a deterministic stub; a production LLM provider is not
  configured.
- **Frontend portal:** prompt submission, PDF upload and date lookup, and a
  live grid statistics dashboard.
- **Container setup:** Dockerfiles and Compose configuration for the backend
  and frontend.
- **Verification:** the full test suite passes (100 tests); the live demo flow
  returns a cache miss followed by a cache hit.
- **Documentation:** [project report](PROJECT_REPORT.md), [final report
  PDF](Internship_Report_Final.pdf), demo guide, daily work sheets, and this
  release summary.

## Run the demo

With Docker Compose, run `docker compose up --build` from the repository root;
the API is available on port 8000 and the frontend on port 5173.

Alternatively, start the backend and frontend with `./run_dev.sh`. On Windows,
use Git Bash or WSL, or follow the separate PowerShell startup commands in
[the demo guide](DEMO_GUIDE.md).

## Known scope

This release is a working project prototype. Prompt inference uses a stub, and
the node router assigns normalized keys with a stable hash modulo the configured
node count; it is not a hash-ring implementation.
