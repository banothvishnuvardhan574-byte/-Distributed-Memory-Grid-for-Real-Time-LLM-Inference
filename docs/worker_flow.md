# Worker Process and Communication

**Role:** Nikhila

## 1. Purpose

The worker receives a job from the API, validates the prompt, processes it using the inference function, and returns a result or a safe error message.

## 2. Worker Flow

1. **Receive job:** Receive the request ID and prompt.
2. **Validate request:** Remove leading and trailing whitespace from the prompt and reject an empty prompt.
3. **Process prompt:** Run the inference function in a separate process.
4. **Handle errors:** Handle inference failures and stop inference if it exceeds the configured timeout.
5. **Return result:** Return the request ID, processing status, and response information.

## 3. Agreed JSON Request Format

The API sends the following information to the worker:

```json
{
  "request_id": "req-123",
  "prompt": "Explain Python"
}
```

- `request_id`: Identifies the original request.
- `prompt`: Contains the user's input text.

## 4. Agreed JSON Response Format

### Successful response

```json
{
  "request_id": "req-123",
  "status": "completed",
  "response": "Python is a programming language.",
  "error": null
}
```

### Failed response

```json
{
  "request_id": "req-123",
  "status": "failed",
  "response": null,
  "error": "Inference timed out"
}
```

- `request_id`: Identifies the original request.
- `status`: Indicates whether processing completed or failed.
- `response`: Contains the generated result on success; it is `null` on failure.
- `error`: Is `null` on success and contains a safe error message on failure.

**Note:** This is the agreed communication format. The worker implementation must be checked against it during integration.

## 5. Timeout and Failure Handling

- Reject prompts that are empty after trimming whitespace.
- Use a configurable timeout to avoid waiting indefinitely for inference.
- Return a failed status when inference raises an exception or times out.
- Include the request ID in the result.
- Return a safe error message without exposing internal exception details.

## 6. Current Implementation Status

The worker module and its tests have been implemented.

The current worker:
- Trims leading and trailing whitespace from prompts.
- Rejects empty prompts.
- Runs inference in a separate process.
- Handles inference exceptions.
- Terminates inference when the configured timeout is exceeded.
- Returns a request ID, status, and response message.

**Integration note:** The current worker response does not yet fully match the agreed JSON format. It returns the failure message in `response` and does not include a separate `error` field. The worker also needs to be connected to the API's inference flow.

The current API accepts prompts but does not yet connect them to actual LLM inference.

## 7. Testing

The worker tests were run using:

```powershell
.\.venv\Scripts\python.exe -m pytest tests/test_worker.py -v
```

**Last recorded result:** 5 tests passed.

Run the command again after making changes to verify the current result.

## 8. Next Steps

1. Review the worker's response fields against the agreed JSON format.
2. Complete API and worker integration when the team is ready.
3. Run the worker tests and relevant project tests.
4. Commit and push the completed changes for team-leader review.

