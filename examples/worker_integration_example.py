"""
Minimal worker integration example for Nikhila (nikhila-worker)
Demonstrates how the worker handler calls the public generate_response interface
and surfaces status, errors, and timeouts cleanly.
"""

import sys
import logging
from typing import Dict, Any

from inference import (
    generate_response,
    InvalidPromptError,
    ModelNotReadyError,
    InferenceTimeoutError,
    InferenceError,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("worker_handler")


def handle_worker_job(request: Dict[str, Any]) -> Dict[str, Any]:
    """
    Worker handler simulating request processing from the FastAPI gateway.
    
    Expected Request Schema:
        { "request_id": str, "prompt": str, "max_tokens": Optional[int] }
        
    Returns Completed / Failed Schema aligned with Master Plan Section 3:
        Completed: { "request_id": str, "status": "completed", "response": str, "latency_ms": int }
        Failed:    { "request_id": str, "status": "failed", "error": str }
    """
    request_id = request.get("request_id", "unknown-req")
    prompt = request.get("prompt")
    max_tokens = request.get("max_tokens", 128)

    logger.info(f"Worker received request_id='{request_id}'")

    try:
        # Call public adapter contract
        response_text = generate_response(prompt=prompt, max_tokens=max_tokens, timeout_sec=15.0)
        return {
            "request_id": request_id,
            "status": "completed",
            "response": response_text,
        }

    except InvalidPromptError as e:
        logger.warning(f"Validation failed for request '{request_id}': {e}")
        return {
            "request_id": request_id,
            "status": "failed",
            "error": f"InvalidPrompt: {str(e)}",
        }

    except ModelNotReadyError as e:
        logger.error(f"Inference backend unavailable for request '{request_id}': {e}")
        return {
            "request_id": request_id,
            "status": "failed",
            "error": f"ModelUnavailable: {str(e)}",
        }

    except InferenceTimeoutError as e:
        logger.error(f"Inference timed out for request '{request_id}': {e}")
        return {
            "request_id": request_id,
            "status": "failed",
            "error": "Inference timed out",
        }

    except InferenceError as e:
        logger.error(f"Execution error for request '{request_id}': {e}")
        return {
            "request_id": request_id,
            "status": "failed",
            "error": f"InferenceError: {str(e)}",
        }


if __name__ == "__main__":
    test_job = {
        "request_id": "demo-req-001",
        "prompt": "Explain distributed inference",
        "max_tokens": 64,
    }
    result = handle_worker_job(test_job)
    print(f"Worker Job Output: {result}")
