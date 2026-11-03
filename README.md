# LLM MemoryGrid — Model & Inference Integration

**Component Owner:** Suraj Kotrange  
**Assigned Branch:** `suraj-inference`  
**Execution Window:** 2–14 November 2026  
**Primary Hand-off:** `generate_response(prompt: str) -> str` interface for `nikhila-worker` and `vishnu-backend`.

---

## 1. Overview & Objective

This component provides a lightweight, robust, reproducible local inference pipeline for the LLM MemoryGrid demonstrator. In accordance with the project rules:
* Model execution is isolated behind a single public interface: `generate_response(prompt: str) -> str`.
* The adapter enforces single-instance model loading in memory (no reloading weights per prompt).
* Generation parameters are strictly bounded (max tokens, timeout, and explicit error states).
* Stub/echo outputs are never disguised as real generation.

---

## 2. Hardware Constraints Summary

From empirical host benchmarking on 3 Nov 2026:
* **CPU:** 2 vCPUs (Intel Xeon 6985P-C)
* **RAM:** 7.8 GiB total (~6.7 GiB free)
* **GPU:** None (CPU inference only)
* **Storage:** 18 GiB free disk

**Recommended Model:** `Qwen2.5-0.5B-Instruct` (GGUF Q4_K_M, ~380 MB download, ~650 MB RAM working set).

Full feasibility study available in: [`docs/INFERENCE_OPTIONS.md`](docs/INFERENCE_OPTIONS.md).

---

## 3. Project Structure

```
├── .gitignore
├── docs/
│   └── INFERENCE_OPTIONS.md          # Hardware audit, model benchmarks & Vishnu proposal
├── inference/
│   ├── __init__.py                   # Package exports
│   ├── adapter.py                    # InferenceAdapter class & generate_response contract
│   └── exceptions.py                 # Custom error hierarchy (ModelNotReadyError, etc.)
├── examples/
│   └── worker_integration_example.py # Minimal callable example for Nikhila
└── tests/
    └── test_inference.py             # Unit & contract tests for Sagar's test runner
```

---

## 4. Quick Start & Setup

### Environment Setup
```bash
# Recommended Python version: 3.11+
python3 -m venv .venv
source .venv/bin/activate

# Install runtime dependencies
pip install llama-cpp-python
```

### Running Unit Tests
```bash
python3 -m unittest discover tests
```

### Worker Integration Pattern
```python
from inference import generate_response, ModelNotReadyError, InferenceTimeoutError

try:
    response_text = generate_response("Explain distributed inference", max_tokens=128)
    print("Response:", response_text)
except ModelNotReadyError as e:
    print("Model not loaded:", e)
except InferenceTimeoutError as e:
    print("Timeout:", e)
```
