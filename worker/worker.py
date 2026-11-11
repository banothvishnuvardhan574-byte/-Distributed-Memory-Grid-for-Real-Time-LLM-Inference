from collections.abc import Callable
import atexit
import logging
import math
import multiprocessing as mp
from multiprocessing.connection import Connection
import threading
import time

from inference.exceptions import (
    InferenceError,
    InferenceTimeoutError,
    InvalidPromptError,
    ModelNotReadyError,
)

logger = logging.getLogger(__name__)

InferenceFunction = Callable[[str], str]
DEFAULT_TIMEOUT_SECONDS = 15.0
WORKER_STARTUP_TIMEOUT_SECONDS = 120.0
DEMO_MAX_TOKENS = 64

_worker_lock = threading.Lock()
_worker_process: mp.Process | None = None
_worker_connection: Connection | None = None
_worker_inference_fn: InferenceFunction | None = None


def adapter_inference(prompt: str) -> str:
    """Call Suraj's public adapter using the agreed demo limits."""
    from inference import generate_response

    return generate_response(
        prompt=prompt,
        max_tokens=DEMO_MAX_TOKENS,
        timeout_sec=DEFAULT_TIMEOUT_SECONDS,
    )


def _worker_process_main(
    connection: Connection,
    inference_fn: InferenceFunction,
) -> None:
    """Initialise once, then process jobs sequentially in this child process."""
    try:
        # Load the adapter/model once when this worker starts.
        if inference_fn is adapter_inference:
            from inference import get_adapter

            get_adapter()

        connection.send({"type": "ready"})

    except Exception as exc:
        logger.exception("Worker initialisation failed")

        try:
            connection.send({
                "type": "startup_error",
                "error_type": type(exc).__name__,
                "error": str(exc),
            })
        except (BrokenPipeError, EOFError, OSError):
            pass
        finally:
            connection.close()

        return

    try:
        while True:
            try:
                request = connection.recv()
            except EOFError:
                break

            if request is None:
                break

            request_id, prompt = request
            started_at = time.perf_counter()

            try:
                response_text = inference_fn(prompt)

                if not isinstance(response_text, str):
                    raise TypeError(
                        "Inference function must return a string"
                    )

                result = {
                    "status": "completed",
                    "response": response_text,
                    "error": None,
                }

            except InvalidPromptError as exc:
                result = {
                    "status": "failed",
                    "response": None,
                    "error": f"InvalidPrompt: {exc}",
                }

            except ModelNotReadyError as exc:
                result = {
                    "status": "failed",
                    "response": None,
                    "error": f"ModelUnavailable: {exc}",
                }

            except InferenceTimeoutError:
                result = {
                    "status": "failed",
                    "response": None,
                    "error": "Inference timed out",
                }

            except InferenceError as exc:
                result = {
                    "status": "failed",
                    "response": None,
                    "error": f"InferenceError: {exc}",
                }

            except Exception:
                logger.exception(
                    "Inference failed for request %s",
                    request_id,
                )

                result = {
                    "status": "failed",
                    "response": None,
                    "error": "Failed to process prompt",
                }

            result["latency_ms"] = int(
                (time.perf_counter() - started_at) * 1000
            )

            try:
                connection.send(result)
            except (BrokenPipeError, EOFError, OSError):
                break

    finally:
        connection.close()


def _stop_worker_locked(force: bool = False) -> None:
    """Stop and release the current worker. Caller must hold _worker_lock."""
    global _worker_process
    global _worker_connection
    global _worker_inference_fn

    connection = _worker_connection
    process = _worker_process

    if process is not None:
        if process.is_alive():
            if force:
                process.terminate()

            elif connection is not None:
                try:
                    connection.send(None)
                except (BrokenPipeError, EOFError, OSError):
                    pass

            process.join(timeout=1.0)

            if process.is_alive():
                process.terminate()
                process.join(timeout=1.0)

            if process.is_alive() and hasattr(process, "kill"):
                process.kill()
                process.join(timeout=1.0)

        try:
            process.close()
        except (ValueError, OSError):
            pass

    if connection is not None:
        try:
            connection.close()
        except OSError:
            pass

    _worker_process = None
    _worker_connection = None
    _worker_inference_fn = None


def _ensure_worker_locked(
    inference_fn: InferenceFunction,
) -> Connection:
    """Start a worker or reuse it when the inference callable is unchanged."""
    global _worker_process
    global _worker_connection
    global _worker_inference_fn

    if (
        _worker_process is not None
        and _worker_process.is_alive()
        and _worker_inference_fn is inference_fn
        and _worker_connection is not None
    ):
        return _worker_connection

    if _worker_process is not None or _worker_connection is not None:
        _stop_worker_locked(force=False)

    context = mp.get_context("spawn")

    parent_connection, child_connection = context.Pipe(
        duplex=True
    )

    process = context.Process(
        target=_worker_process_main,
        args=(child_connection, inference_fn),
        name="memorygrid-inference-worker",
        daemon=True,
    )

    try:
        process.start()
    except Exception:
        parent_connection.close()
        child_connection.close()
        raise

    child_connection.close()

    _worker_process = process
    _worker_connection = parent_connection
    _worker_inference_fn = inference_fn

    # Model loading has a separate startup budget.
    # The 15-second inference timeout starts after readiness.
    if not parent_connection.poll(WORKER_STARTUP_TIMEOUT_SECONDS):
        _stop_worker_locked(force=True)
        raise TimeoutError(
            "Worker did not finish starting within 120 seconds"
        )

    try:
        startup_message = parent_connection.recv()

    except (EOFError, OSError) as exc:
        _stop_worker_locked(force=True)
        raise RuntimeError(
            "Worker exited during startup"
        ) from exc

    if (
        not isinstance(startup_message, dict)
        or startup_message.get("type") != "ready"
    ):
        error_type = (
            startup_message.get(
                "error_type",
                "WorkerStartupError",
            )
            if isinstance(startup_message, dict)
            else "WorkerStartupError"
        )

        error = (
            startup_message.get(
                "error",
                "Worker sent an invalid startup message",
            )
            if isinstance(startup_message, dict)
            else "Worker sent an invalid startup message"
        )

        _stop_worker_locked(force=True)

        raise RuntimeError(f"{error_type}: {error}")

    return parent_connection


def _failure_result(
    request_id: str,
    error: str,
    started_at: float,
) -> dict[str, str | None | int]:

    return {
        "request_id": request_id,
        "status": "failed",
        "response": None,
        "error": error,
        "latency_ms": int(
            (time.perf_counter() - started_at) * 1000
        ),
    }


def process_prompt(
    request_id: str,
    prompt: str,
    inference_fn: InferenceFunction,
    timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
) -> dict[str, str | None | int]:
    """Run a prompt in a persistent process with a hard parent-side timeout.

    Calls are serialised because one worker process handles one inference
    at a time. A timed-out or crashed worker is stopped and replaced on
    the next call.

    On Windows, inference functions must be importable top-level functions.
    """

    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt cannot be empty")

    try:
        timeout = float(timeout_seconds)

    except (TypeError, ValueError):
        raise ValueError(
            "Timeout must be greater than zero"
        ) from None

    if not math.isfinite(timeout) or timeout <= 0:
        raise ValueError("Timeout must be greater than zero")

    if not callable(inference_fn):
        raise ValueError("inference_fn must be callable")

    clean_prompt = prompt.strip()
    started_at = time.perf_counter()

    if not _worker_lock.acquire(timeout=timeout):
        return _failure_result(
            request_id,
            "Inference timed out",
            started_at,
        )

    try:
        try:
            connection = _ensure_worker_locked(inference_fn)

            connection.send((request_id, clean_prompt))

        except Exception as exc:
            logger.exception(
                "Could not start or communicate with worker"
            )

            _stop_worker_locked(force=True)

            message = str(exc)

            if "ModelNotReadyError" in message:
                message = f"ModelUnavailable: {message}"
            else:
                message = "Worker process failed"

            return _failure_result(
                request_id,
                message,
                started_at,
            )

        if not connection.poll(timeout):
            logger.error(
                "Request %s timed out",
                request_id,
            )

            _stop_worker_locked(force=True)

            return _failure_result(
                request_id,
                "Inference timed out",
                started_at,
            )

        try:
            worker_result = connection.recv()

        except (EOFError, OSError):
            logger.exception(
                "Worker process stopped before returning a result"
            )

            _stop_worker_locked(force=True)

            return _failure_result(
                request_id,
                "Worker process failed",
                started_at,
            )

        if not isinstance(worker_result, dict):
            _stop_worker_locked(force=True)

            return _failure_result(
                request_id,
                "Worker returned an invalid result",
                started_at,
            )

        return {
            "request_id": request_id,
            **worker_result,
        }

    finally:
        _worker_lock.release()


def shutdown_worker() -> None:
    """Gracefully stop the persistent worker during application shutdown."""

    with _worker_lock:
        _stop_worker_locked(force=False)


atexit.register(shutdown_worker)