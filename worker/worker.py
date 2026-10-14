
import logging
import multiprocessing
import queue
from collections.abc import Callable


logger = logging.getLogger(__name__)


def _run_inference(result_queue, inference_fn, prompt):
    """Run inference in a separate process and return its result."""
    try:
        response = inference_fn(prompt)
        result_queue.put(("completed", response))
    except Exception:
        result_queue.put(("failed", "Failed to process prompt"))


def process_prompt(
    request_id: str,
    prompt: str,
    inference_fn: Callable[[str], str],
    timeout_seconds: float = 5.0,
) -> dict[str, str]:
    """Process a prompt with process-based timeout handling."""

    clean_prompt = prompt.strip()

    if not clean_prompt:
        raise ValueError("Prompt cannot be empty")

    if timeout_seconds <= 0:
        raise ValueError("Timeout must be greater than zero")

    logger.info("Processing request %s", request_id)

    context = multiprocessing.get_context("spawn")
    result_queue = context.Queue()
    process = context.Process(
        target=_run_inference,
        args=(result_queue, inference_fn, clean_prompt),
    )

    try:
        process.start()
        process.join(timeout_seconds)

        if process.is_alive():
            process.terminate()
            process.join()
            logger.error("Request %s timed out", request_id)

            return {
                "request_id": request_id,
                "status": "failed",
                "response": "Inference timed out",
            }

        try:
            status, response = result_queue.get(timeout=0.5)
        except queue.Empty:
            status, response = "failed", "Failed to process prompt"

        if status == "completed":
            logger.info("Request %s completed", request_id)
        else:
            logger.error("Request %s failed", request_id)

        return {
            "request_id": request_id,
            "status": status,
            "response": response,
        }

    except Exception:
        logger.exception("Request %s failed", request_id)
        return {
            "request_id": request_id,
            "status": "failed",
            "response": "Failed to process prompt",
        }

    finally:
        if process.is_alive():
            process.terminate()
            process.join()

        result_queue.close()
        result_queue.join_thread()
