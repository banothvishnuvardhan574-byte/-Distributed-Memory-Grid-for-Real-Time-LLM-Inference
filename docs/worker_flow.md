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
- `timeout_seconds`: The maximum allowed inference wait time.

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

The worker response contract is separate from the existing FastAPI response model. The FastAPI `PromptResponse` model currently does not expose `latency_ms`.

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

The worker initialisation readiness timeout is 120 seconds. This allows time for inference environment initialisation.

The normal inference timeout defaults to 15 seconds.

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

Explicit FastAPI startup and shutdown lifecycle integration remains a follow-up task.

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

When `adapter_inference` is supplied, the worker obtains the adapter singleton during child-process initialisation.

The adapter is intended to retain its model instance within the persistent process, avoiding normal per-request model reloads.

**Important:** Obtaining the adapter singleton does not guarantee that model weights are loaded. A valid model path and the required runtime must be available.

The current FastAPI application still supplies its local `stub_inference` function. Therefore, real API-to-model inference integration has not yet been completed.

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

The FastAPI application continues to use its local stub inference function. Real LLM inference through the API remains pending team integration and model availability.

## 10. Testing

### Focused worker tests

Command:

```powershell
python -m pytest tests/test_worker.py -v
```

**Latest recorded result: 13 passed.**

Coverage includes:

- Successful inference.
- Inference failure.
- Prompt whitespace cleanup.
- Empty prompt validation.
- Timeout handling.
- Invalid timeout validation.
- Persistent process reuse.
- Worker restart after timeout.
- Typed inference exception handling.

### API worker tests

Command:

```powershell
python -m pytest tests/test_api_worker.py -v
```

**Latest recorded result: 2 passed, 2 warnings.**

### Complete project test suite

Command:

```powershell
python -m pytest -q
```

**Latest recorded result: 115 passed, 2 warnings in 10.20 seconds.**

These results were recorded after the persistent worker implementation.

## 11. Git Record

**Branch:** `nikhila-worker`

**Worker implementation commit:**

`b852c81`

**Commit message:**

`feat(worker): add persistent inference process`

The implementation and worker tests were committed in this commit.

## 12. Remaining Work

1. Coordinate real inference integration with Suraj and Vishnu.
2. Connect the approved inference adapter to the API through the agreed integration point.
3. Add explicit FastAPI startup and shutdown worker lifecycle integration with Vishnu's approval.
4. Verify real inference using an available model.
5. Confirm the final API response contract, including whether `latency_ms` should be exposed.
6. Run full regression and integration tests.
7. Submit the documentation and implementation for team review.

**Scope limitation:** Remote gRPC communication and advanced distributed worker execution are not claimed as completed by this local persistent-worker implementation.
