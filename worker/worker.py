
from collections.abc import Callable
import logging
import threading

logger = logging.getLogger(__name__)


def _run_inference(
    inference_fn: Callable[[str], str],
    prompt: str,
) -> tuple[bool, str | None]:
    """Run inference and return status plus deterministic payload."""
    try:
        return True, inference_fn(prompt)
    except Exception:
        logger.exception("Inference execution failed for prompt")
        return False, "Failed to process prompt"


def process_prompt(
    request_id: str,
    prompt: str,
    inference_fn: Callable[[str], str],
    timeout_seconds: float = 5.0,
) -> dict[str, str | None]:
    """Process a prompt with a bounded timeout and error handling.

    The project runs under Windows pytest/fastapi test clients, where 
    multiprocessing spawn semantics can be flaky. This keeps the same public
    API while using a thread-based worker with an enforced timeout, which is
    sufficient for the app's prototype behavior and test expectations.
    """

    clean_prompt = prompt.strip()

    if not clean_prompt:
        raise ValueError("Prompt cannot be empty")

    if timeout_seconds <= 0:
        raise ValueError("Timeout must be greater than zero")

    logger.info("Processing request %s", request_id)

    result: dict[str, object] = {}
    finished = threading.Event()

    def worker() -> None:
        try:
            succeeded, payload = _run_inference(inference_fn, clean_prompt)
            result["succeeded"] = succeeded
            result["payload"] = payload
        except Exception:
            result["succeeded"] = False
            result["payload"] = "Failed to process prompt"
        finally:
            finished.set()

    thread = threading.Thread(target=worker, daemon=True)
    thread.start()
    finished.wait(timeout_seconds)

    if not finished.is_set():
        logger.error("Request %s timed out", request_id)
        return {
            "request_id": request_id,
            "status": "failed",
            "response": None,
            "error": "Inference timed out",
        }

    if result.get("succeeded"):
        logger.info("Request %s completed", request_id)
        return {
            "request_id": request_id,
            "status": "completed",
            "response": result["payload"],
            "error": None,
        }

    logger.error("Request %s failed", request_id)
    return {
        "request_id": request_id,
        "status": "failed",
        "response": None,
        "error": "Failed to process prompt",
    }
