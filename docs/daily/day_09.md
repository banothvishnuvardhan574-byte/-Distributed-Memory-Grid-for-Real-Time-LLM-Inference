# Day 9 — Prompt response and failure handling

## Completed

- The prompt endpoint publishes the `PromptResponse` schema in OpenAPI.
- Empty prompts return HTTP 400; worker failures return HTTP 500 with a useful
  detail.
- PDF date matching covers abbreviated/full month names and numeric formats;
  empty or invalid PDF data is rejected safely.
- LRU eviction and TTL expiry are covered under load and at the expiry boundary.
- The prompt form exposes loading progress and submission errors.

## Verification

```text
python -m pytest tests/ -v
python -m pytest tests/ -k "evict or ttl" -v
python -m pytest tests/ -k fail -v
```

The prompt endpoint's response schema is checked in the generated OpenAPI
document (`/docs`).
