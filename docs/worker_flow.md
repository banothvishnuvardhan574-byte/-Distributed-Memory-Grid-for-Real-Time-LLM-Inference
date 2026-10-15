# Worker Process and Communication

**Role:** Nikhila

## 1. Purpose

The worker receives a job from the API, validates the request, processes the prompt using the inference function, and returns a result or an error.

## 2. Worker Flow

1. **Receive job:** Receive the request ID and prompt from the API.
2. **Validate request:** Check that the request ID is present and the prompt is not empty.
3. **Process prompt:** Send the validated prompt to the inference function.
4. **Handle errors:** Handle inference failures and timeouts.
5. **Return result:** Return the request ID, status, and response or error.

## 3. Proposed JSON Request Format

The API sends this information to the worker:

```json
{
  "request_id": "req-123",
  "prompt": "Explain Python"
}
```

- `request_id`: Identifies the request.
- `prompt`: Contains the user's input text.

## 4. Proposed JSON Response Format

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
- `response`: Contains the generated result when successful.
- `error`: Contains an error message when processing fails.

**Note:** This JSON structure is a proposal and must be agreed upon by the API, worker, and inference teammates before integration.

## 5. Timeout and Failure Handling

- Reject requests with an empty prompt.
- Use a timeout to avoid waiting indefinitely for inference.
- Return a failed status if inference raises an error or times out.
- Include the request ID in the response.
- Return a safe error message without exposing sensitive information.

## 6. Current Implementation Status

The worker module and its tests have been implemented. The worker still needs to be checked against the team's agreed communication format and connected to the actual inference interface.

The current API accepts prompts but does not yet connect them to actual LLM inference.



## 8. Next Steps

1. Review the proposed JSON structure with the team.
2. Finalize the request and response formats.
3. Update the worker implementation and tests if needed.
4. Test the worker and API integration.