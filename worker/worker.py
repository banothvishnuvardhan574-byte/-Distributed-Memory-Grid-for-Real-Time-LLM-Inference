
from collections.abc import Callable
from concurrent.futures import ThreadPoolExecutor, TimeoutError
import logging


logger = logging.getLogger(__name__)


def process_prompt(
    request_id: str,
    prompt: str,
    inference_fn: Callable[[str], str],
    timeout_seconds: float = 5.0,
) -> dict[str, str]:
    """Process a prompt with basic timeout and error handling."""

    clean_prompt = prompt.strip()

    if not clean_prompt:
        raise ValueError("Prompt cannot be empty")

    logger.info("Processing request %s", request_id)

    executor = ThreadPoolExecutor(max_workers=1)
    future = executor.submit(inference_fn, clean_prompt)

    try:
        result = future.result(timeout=timeout_seconds)

        logger.info("Request %s completed", request_id)

        return {
            "request_id": request_id,
            "status": "completed",
            "response": result,
        }

    except TimeoutError:
        future.cancel()
        logger.error("Request %s timed out", request_id)

        return {
            "request_id": request_id,
            "status": "failed",
            "response": "Inference timed out",
        }

    except Exception:
        logger.exception("Request %s failed", request_id)

        return {
            "request_id": request_id,
            "status": "failed",
            "response": "Failed to process prompt",
        }

    finally:
        executor.shutdown(wait=False, cancel_futures=True)
