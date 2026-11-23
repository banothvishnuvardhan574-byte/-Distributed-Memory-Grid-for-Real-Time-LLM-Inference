# Worker Process and Communication

**Owner:** Nikhila
**Role:** Worker Process & Communication Engineer
**Branch:** `nikhila-worker`

## 1. Purpose

The worker receives a job from the API, validates the prompt, executes the supplied inference function in a persistent child process, and returns a structured success or failure result.

The main objectives are:

- Preserve the original request ID.
- Reuse a worker process across successive requests.
- Avoid loading the inference model again for every normal request.
- Enforce bounded inference execution.
- Terminate and clean up a worker that times out.
- Return structured errors without exposing unexpected internal tracebacks.

## 2. Worker Architecture

The worker uses Python multiprocessing with the Windows-compatible `spawn` start method.

The processing flow is:

1. **Receive job:** `process_prompt()` receives the request ID, prompt, inference function, and timeout.
2. **Validate request:** Trim leading and trailing whitespace and reject empty prompts.
3. **Start or reuse worker:** Reuse the existing process when the same inference function is supplied. Otherwise, stop the previous worker and start a replacement.
4. **Initialise worker:** The child process initialises its inference environment and sends a readiness message.
5. **Execute inference:** Receive the job through a multiprocessing Pipe and execute it in the child process.
6. **Handle errors:** Return structured failures for known inference exceptions and unexpected errors.
7. **Enforce timeout:** The parent process waits for the configured inference timeout. If the worker does not respond, terminate and clean up that process.
8. **Return result:** Include the request ID, status, response, error, and latency.
9. **Reuse or restart:** Reuse a healthy worker for subsequent requests. Start a replacement after a timeout or process failure.

Requests are serialised using a thread lock because one worker process handles one inference request at a time.

The worker starts lazily when the first prompt is submitted. When the adapter inference function is used, the child process obtains the inference adapter singleton before announcing that it is ready.

## 3. Worker Request Contract

The public worker entry point is:

`process_prompt(request_id, prompt, inference_fn, timeout_seconds=15.0)`

The logical request contains:

```json
{
  "request_id": "req-123",
  "prompt": "Explain Python"
}
```

The parent process sends the request ID and cleaned prompt to the child through a multiprocessing Pipe.

The internal IPC message is a Python tuple:

`(request_id, clean_prompt)`

Request fields:

- `request_id`: Identifies the original request.
- `prompt`: Contains the user's input text.
- `inference_fn`: The callable used to perform inference.
- `timeout_seconds`: The maximum allowed inference wait time after worker startup.

## 4. Worker Response Contract

### Successful response

```json
{
  "request_id": "req-123",
  "status": "completed",
  "response": "Python is a programming language.",
  "error": null,
  "latency_ms": 120
}
```

### Failed response

```json
{
  "request_id": "req-123",
  "status": "failed",
  "response": null,
  "error": "Inference timed out",
  "latency_ms": 15000
}
```

Response fields:

- `request_id`: Identifies the original request.
- `status`: Indicates whether processing completed or failed.
- `response`: Contains generated output on success; `null` on failure.
- `error`: Contains `null` on success or an error description on failure.
- `latency_ms`: Records the worker-side processing time in milliseconds.

The FastAPI `PromptResponse` model exposes `latency_ms`. The API uses the worker's latency value when one is returned; the response model defaults the field to `0` when the result does not include it (for example, a cache hit).

## 5. Persistent Process Management

The worker maintains module-level references to:

- The child process.
- The parent-side Pipe connection.
- The inference function associated with that process.

When another request arrives with the same inference function, the existing healthy process is reused.

If the inference function changes, the existing worker is stopped before starting another one.

The worker uses:

- `multiprocessing.get_context("spawn")`
- `multiprocessing.Process`
- `multiprocessing.Pipe`
- `threading.Lock`

The worker initialisation readiness timeout is 120 seconds. This allows time for inference environment initialisation. The normal inference timeout defaults to 15 seconds and begins after the worker reports that it is ready.

### Timeout recovery

If inference does not respond within the configured timeout:

1. Terminate the child process.
2. Wait for process termination.
3. Force-kill the process if required and supported.
4. Close the process and communication resources.
5. Return a failed result.
6. Start a replacement worker when the next request arrives.

The worker does not attempt to reuse a process that has timed out.

### Shutdown

The module provides:

`shutdown_worker()`

This function attempts graceful shutdown and then terminates the process if necessary.

An `atexit` handler also registers worker cleanup when the parent Python process exits.

The FastAPI application now uses the lifespan mechanism in `app/main.py`. Its `finally` block calls `shutdown_worker()` when the application shuts down, connecting worker cleanup to the API lifecycle.

## 6. Inference Adapter Integration

The worker includes an adapter wrapper:

`adapter_inference(prompt)`

It calls Suraj's public inference interface:

```python
generate_response(
    prompt=prompt,
    max_tokens=64,
    timeout_sec=15.0
)
```

The adapter provides:

- `InvalidPromptError`
- `ModelNotReadyError`
- `InferenceTimeoutError`
- `InferenceError`

When `adapter_inference` is supplied, the worker obtains the adapter singleton during child-process initialisation. The adapter is intended to retain its model instance within the persistent process, avoiding normal per-request model reloads.

In `app/main.py`, the name `stub_inference` is retained as a compatibility hook for existing tests, but it is assigned to `adapter_inference`. The prompt-processing path therefore delegates to the public inference adapter; it is not the old echo-stub implementation.

**Runtime limitation:** Connecting the adapter in code does not by itself prove that genuine model generation is available. The verified local environment used for this PR did not have `llama-cpp-python` installed and did not have `LLM_MODEL_PATH` configured. Genuine model output therefore remains to be demonstrated after the agreed runtime and model file are installed and configured. Model weights and other large model artifacts must not be committed to Git.

## 7. Error Handling

The worker distinguishes the following inference failures:

| Exception | Worker error |
|---|---|
| `InvalidPromptError` | `InvalidPrompt: ...` |
| `ModelNotReadyError` | `ModelUnavailable: ...` |
| `InferenceTimeoutError` | `Inference timed out` |
| `InferenceError` | `InferenceError: ...` |
| Unexpected exception | `Failed to process prompt` |

Empty prompts and invalid timeout values are rejected before inference begins.

Failures return `status: failed` and `response: null`.

## 8. Windows Compatibility

The worker uses the multiprocessing `spawn` method.

Inference functions supplied to the worker must be importable, top-level Python functions. Lambdas and locally defined functions are not suitable for this multiprocessing interface on Windows.

The test suite uses top-level fake inference functions to verify this behaviour.

## 9. Current Implementation Status

The persistent worker implementation is committed on the `nikhila-worker` branch.

Implemented capabilities:

- Prompt trimming and empty-prompt validation.
- Persistent worker process.
- Request communication through a multiprocessing Pipe.
- Reuse of a healthy worker process.
- Parent-side timeout enforcement.
- Worker termination and cleanup after timeout.
- Automatic worker replacement on the next request.
- Structured success and failure results.
- Typed inference exception handling.
- Processing latency measurement.
- Explicit worker shutdown function.
- FastAPI lifespan shutdown integration.
- FastAPI connection to the public inference adapter.
- API response field for `latency_ms`.

The code path is connected to the inference adapter, but genuine model generation is not yet verified because the local runtime and model path were not configured during the recorded test run.

## 10. Testing

### Focused worker tests

Command:

```powershell
python -m pytest tests/test_worker.py -v
```

Worker test coverage includes:

- Successful inference.
- Inference failure.
- Prompt whitespace cleanup.
- Empty prompt validation.
- Timeout handling.
- Invalid timeout validation.
- Persistent process reuse.
- Worker restart after timeout.
- Typed inference exception handling.

### Complete project test suite

Command:

```powershell
python -m pytest -q
```

**Earlier pre-merge result: 117 passed in 23.21 seconds. See Section 13 for the latest post-merge regression result.**

Python syntax was also checked with:

```powershell
python -m py_compile app\main.py
```

The command completed with no output, indicating no syntax error in `app/main.py`.

These automated tests use fake inference for deterministic test coverage. They do not replace a real-model end-to-end inference demonstration.

## 11. Git Record

**Branch:** `nikhila-worker`

**Worker implementation commit:**

`b852c81`

**Commit message:**

`feat(worker): add persistent inference process`

The worker implementation and API integration were merged into `main` through Pull Request #81.

## 12. Remaining Work

1. Coordinate the chat-template improvement with Suraj.
2. Repeat the API-to-worker-to-model integration test after the adapter update.
3. Verify that the generated response is relevant to the software prompt.
4. Run the full regression suite after the adapter change.
5. Record the final integration evidence.

**Scope limitation:** Remote gRPC communication, multi-machine execution, and advanced distributed inference are not claimed as completed by this local persistent-worker implementation.


## 13. Post-Merge Real-Model Verification

**Verification date:** 7 November 2026

After Pull Request #81 was merged into `main`, the local environment was
updated and genuine model inference was tested.

### Runtime and model setup

- Installed `llama-cpp-python` version `0.3.36`.
- Used a prebuilt Windows CPU wheel.
- Downloaded Qwen2.5-0.5B-Instruct in GGUF Q4_K_M format.
- Model file: `models/qwen2.5-0.5b-instruct-q4_k_m.gguf`.
- Verified file size: approximately 468.6 MiB.
- Verified GGUF file header.
- Configured `LLM_MODEL_PATH` in the local PowerShell session.
- Model weights remain local and are excluded from Git.

### Model loading test

Command:

```powershell
python -c "from inference import get_adapter; a=get_adapter(); print('Model loaded:', a.is_loaded); print('Model metadata:', a.model_metadata)"
```

**Observed result:**

- Model loaded: `True`
- Device: CPU
- Threads: 2
- Model loading time: 0.853 seconds.

### Direct inference adapter test

The public `generate_response()` interface successfully generated genuine model output.

Observed generation time: approximately 1.62 seconds.

### API-to-worker-to-model integration test

The FastAPI server was started with a temporary local API key and the configured model path.

A prompt was submitted to `POST /api/prompt` from a second terminal.

**Observed result:**

- Request ID: `7b2a0a51-3fb8-4f34-912e-4a04a887b0ce`
- Status: `completed`
- Cache: `miss`
- Error: `null`
- Worker latency: 937 ms
- Genuine model-generated response returned through the API.

The response was not semantically appropriate to the software-related question. Successful execution does not guarantee satisfactory response quality.

### Chat-template comparison

A separate direct test using `create_chat_completion()` with a user-role message produced a more relevant response.

This suggests that using the Qwen chat template may improve instruction-following quality.

The production adapter still requires review by Suraj, its owner. No production adapter change is claimed here.

### Updated regression test result

After updating the local branch to the latest `main`:

Command:

```powershell
python -m pytest -q
```

**Earlier observed result (before 9 November 2026): 127 passed in 22.81 seconds.**

The automated test suite and genuine model integration test were performed separately. The 127 passing tests do not represent a 127-test real-model inference run.


## 14. Latest Main Sync and Regression Verification

**Verification date:** 9 November 2026

### Latest main integration

The local `nikhila-worker` branch was updated with the latest `origin/main` commit:

- Main commit: `4fa12a2`
- Update method: Fast-forward merge.
- The update included API-side prompt coalescing.
- Added test file: `tests/test_prompt_coalescing.py`.

### Prompt coalescing

The updated backend supports sharing one inference operation between concurrent identical prompts.

The new tests verify:
- Concurrent identical prompts share one inference operation.
- Inference failures reach waiting requests, and a subsequent retry can succeed.

The existing Worker interface remains compatible. No direct changes to `worker/worker.py` were required for this update.

### Latest regression test

Command:

```powershell
python -m pytest -q

```

**Observed result: 129 passed in 22.60 seconds.**

The full automated regression suite passed after synchronising with the latest main branch.

### Git verification

The comparison between `origin/main` and the local branch returned:

```text
0    0
```

This confirms that the local branch contains the same commit history as the latest main branch at the time of verification.