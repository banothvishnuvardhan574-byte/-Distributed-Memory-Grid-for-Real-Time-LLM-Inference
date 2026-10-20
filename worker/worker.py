
from collections.abc import Callable
import logging
import multiprocessing
from multiprocessing.connection import Connection

logger = logging.getLogger(__name__)


def _run_inference(
    connection: Connection,
    inference_fn: Callable[[str], str],
    prompt: str,
) -> None:
    """Run inference in a separate process and send back its result."""
    try:
        connection.send((True, inference_fn(prompt)))
    except Exception:
        connection.send((False, "Failed to process prompt"))
    finally:
        connection.close()


def process_prompt(
    request_id: str,
    prompt: str,
    inference_fn: Callable[[str], str],
    timeout_seconds: float = 5.0,
) -> dict[str, str | None]:
    """Process a prompt with process-based timeout and error handling."""

    clean_prompt = prompt.strip()

    if not clean_prompt:
        raise ValueError("Prompt cannot be empty")

    if timeout_seconds <= 0:
        raise ValueError("Timeout must be greater than zero")

    logger.info("Processing request %s", request_id)

    receive_connection, send_connection = multiprocessing.Pipe(duplex=False)
    process = multiprocessing.Process(
        target=_run_inference,
        args=(send_connection, inference_fn, clean_prompt),
    )

    try:
        process.start()
        send_connection.close()

        if not receive_connection.poll(timeout_seconds):
            logger.error("Request %s timed out", request_id)
            process.terminate()
            process.join()

            return {
                "request_id": request_id,
                "status": "failed",
                "response": None,
                "error": "Inference timed out",
            }

        succeeded, result = receive_connection.recv()
        process.join()

        if succeeded:
            logger.info("Request %s completed", request_id)
            return {
                "request_id": request_id,
                "status": "completed",
                "response": result,
                "error": None,
            }

        logger.error("Request %s failed", request_id)
        return {
            "request_id": request_id,
            "status": "failed",
            "response": None,
            "error": "Failed to process prompt",
        }

    except Exception:
        logger.exception("Request %s failed", request_id)

        if process.is_alive():
            process.terminate()
            process.join()

        return {
            "request_id": request_id,
            "status": "failed",
            "response": None,
            "error": "Failed to process prompt",
        }

    finally:
        receive_connection.close()
        if process.is_alive():
            process.terminate()
            process.join()
