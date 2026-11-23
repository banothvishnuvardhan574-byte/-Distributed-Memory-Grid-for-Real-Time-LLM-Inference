"""Reproducible API and local inference measurements for the MemoryGrid demo."""

from __future__ import annotations

import argparse
import ctypes
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
from uuid import uuid4

import httpx


PROMPTS = (
    "What is the capital of France?",
    "Summarize in one sentence: AI is changing software development.",
    "Write a short greeting for a new teammate.",
    "List three benefits of distributed memory for LLM systems.",
    "Explain caching in one paragraph.",
)

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


def _total_memory_bytes() -> int | None:
    if platform.system() == "Windows":
        class MemoryStatus(ctypes.Structure):
            _fields_ = [
                ("length", ctypes.c_ulong),
                ("memory_load", ctypes.c_ulong),
                ("total_phys", ctypes.c_ulonglong),
                ("avail_phys", ctypes.c_ulonglong),
                ("total_page_file", ctypes.c_ulonglong),
                ("avail_page_file", ctypes.c_ulonglong),
                ("total_virtual", ctypes.c_ulonglong),
                ("avail_virtual", ctypes.c_ulonglong),
                ("avail_extended_virtual", ctypes.c_ulonglong),
            ]

        status = MemoryStatus()
        status.length = ctypes.sizeof(status)
        if ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(status)):
            return status.total_phys
        return None

    if hasattr(os, "sysconf"):
        try:
            return os.sysconf("SC_PAGE_SIZE") * os.sysconf("SC_PHYS_PAGES")
        except (OSError, ValueError):
            return None
    return None


def _package_version(package: str) -> str | None:
    try:
        return importlib.metadata.version(package)
    except importlib.metadata.PackageNotFoundError:
        return None


def _command_version(command: str) -> str | None:
    windows_script = os.name == "nt" and command == "npm"
    args = f"{command}.cmd --version" if windows_script else [command, "--version"]
    try:
        result = subprocess.run(
            args,
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=5,
            shell=windows_script,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return (result.stdout or result.stderr).strip().splitlines()[0]


def _frontend_package_versions() -> dict[str, str | None]:
    lock_path = ROOT / "frontend" / "package-lock.json"
    try:
        lock = json.loads(lock_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    packages = lock.get("packages", {})
    names = ("react", "react-dom", "vite", "oxlint", "@mui/material")
    return {
        name: packages.get(f"node_modules/{name}", {}).get("version")
        for name in names
    }


def _git_value(*args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=ROOT,
            check=True,
            capture_output=True,
            text=True,
            timeout=2,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def _source_fingerprint() -> str | None:
    try:
        diff = subprocess.run(
            ["git", "diff", "HEAD", "--binary"],
            cwd=ROOT,
            check=True,
            capture_output=True,
            timeout=5,
        ).stdout
    except (OSError, subprocess.SubprocessError):
        diff = b""

    script = Path(__file__).read_bytes()
    return hashlib.sha256(diff + b"\0performance_demo.py\0" + script).hexdigest()


def environment(model_path: str | None) -> dict:
    memory = _total_memory_bytes()
    model_file = Path(model_path) if model_path else None
    model_exists = model_file.is_file() if model_file else False
    model_sha256 = None
    if model_exists:
        digest = hashlib.sha256()
        with model_file.open("rb") as model:
            for chunk in iter(lambda: model.read(1024 * 1024), b""):
                digest.update(chunk)
        model_sha256 = digest.hexdigest()
    git_status = _git_value("status", "--porcelain")
    return {
        "os": platform.platform(),
        "python": platform.python_version(),
        "architecture": platform.machine(),
        "cpu": platform.processor() or "not reported by operating system",
        "physical_memory_bytes": memory,
        "gpu": "not queried",
        "packages": {
            name: _package_version(name)
            for name in (
                "fastapi",
                "httpx",
                "pydantic",
                "pydantic-settings",
                "uvicorn",
                "pypdf",
                "llama-cpp-python",
                "pytest",
            )
        },
        "frontend_tools": {
            "node": _command_version("node"),
            "npm": _command_version("npm"),
        },
        "frontend_locked_packages": _frontend_package_versions(),
        "git_commit": _git_value("rev-parse", "HEAD"),
        "git_branch": _git_value("branch", "--show-current"),
        "git_worktree_dirty": None if git_status is None else bool(git_status),
        "source_fingerprint_sha256": _source_fingerprint(),
        "model_file_configured": bool(model_path),
        "model_file_name": model_file.name if model_file else None,
        "model_file_exists": model_exists,
        "model_file_size_bytes": model_file.stat().st_size if model_exists else None,
        "model_file_sha256": model_sha256,
        "generation": {
            "runtime": "llama-cpp-python adapter",
            "streaming": False,
            "max_new_tokens": None,
            "timeout_seconds": None,
            "warmup_per_prompt": None,
            "measured_runs_per_prompt": None,
        },
    }


def summarize(samples: list[dict]) -> dict:
    latencies = [sample["latency_ms"] for sample in samples if sample.get("latency_ms") is not None]
    ordered = sorted(latencies)
    p95 = ordered[max(0, math.ceil(0.95 * len(ordered)) - 1)] if ordered else None
    successes = sum(sample["status"] == "success" for sample in samples)
    failures = sum(sample["status"] == "failure" for sample in samples)
    return {
        "attempts": len(samples),
        "successes": successes,
        "failures": failures,
        "success_rate_percent": round(successes * 100 / len(samples), 2) if samples else None,
        "latency_ms": {
            "mean": round(statistics.mean(latencies), 3) if latencies else None,
            "median": round(statistics.median(latencies), 3) if latencies else None,
            "p95_nearest_rank": round(p95, 3) if p95 is not None else None,
            "min": round(min(latencies), 3) if latencies else None,
            "max": round(max(latencies), 3) if latencies else None,
        },
    }


def _api_prompt(base_prompt: str, label: str, sample_number: int) -> str:
    return f"{base_prompt}\nBenchmark sample {label}-{sample_number}-{uuid4().hex}"


def measure_api(
    base_url: str,
    runs: int,
    warmup: int,
    timeout: float,
) -> dict:
    samples = []
    warmup_failures = []
    prompts = []
    try:
        with httpx.Client(base_url=base_url, timeout=timeout) as client:
            for prompt_index, prompt in enumerate(PROMPTS, start=1):
                for warmup_index in range(1, warmup + 1):
                    try:
                        response = client.post(
                            "/api/prompt",
                            json={"prompt": _api_prompt(prompt, "warmup", warmup_index)},
                        )
                        try:
                            body = response.json()
                        except ValueError:
                            body = None
                        if (
                            response.status_code != 200
                            or not isinstance(body, dict)
                            or not body.get("request_id")
                        ):
                            warmup_failures.append({
                                "prompt_index": prompt_index,
                                "http_status": response.status_code,
                                "error": response.text[:500],
                            })
                    except httpx.HTTPError as exc:
                        warmup_failures.append({
                            "prompt_index": prompt_index,
                            "error": f"{type(exc).__name__}: {exc}",
                        })

                for run_index in range(1, runs + 1):
                    request_prompt = _api_prompt(prompt, "measured", run_index)
                    prompts.append({
                        "prompt_index": prompt_index,
                        "base_prompt": prompt,
                        "request_prompt": request_prompt,
                    })
                    started = time.perf_counter()
                    try:
                        response = client.post(
                            "/api/prompt",
                            json={"prompt": request_prompt},
                        )
                        latency_ms = (time.perf_counter() - started) * 1000
                        body = None
                        try:
                            body = response.json()
                        except ValueError:
                            pass
                        succeeded = (
                            response.status_code == 200
                            and isinstance(body, dict)
                            and bool(body.get("request_id"))
                        )
                        samples.append({
                            "prompt_index": prompt_index,
                            "run_index": run_index,
                            "request_id": body.get("request_id") if isinstance(body, dict) else None,
                            "http_status": response.status_code,
                            "cache": body.get("cache") if isinstance(body, dict) else None,
                            "status": "success" if succeeded else "failure",
                            "latency_ms": round(latency_ms, 3),
                            "error": None if succeeded else response.text[:500],
                        })
                    except httpx.HTTPError as exc:
                        latency_ms = (time.perf_counter() - started) * 1000
                        samples.append({
                            "prompt_index": prompt_index,
                            "run_index": run_index,
                            "request_id": None,
                            "http_status": None,
                            "cache": None,
                            "status": "failure",
                            "latency_ms": round(latency_ms, 3),
                            "error": f"{type(exc).__name__}: {exc}",
                        })
    except httpx.InvalidURL as exc:
        return {
            "status": "blocked",
            "blocked_reason": f"Invalid API base URL: {exc}",
            "summary": summarize(samples),
            "warmup_failures": warmup_failures,
            "samples": samples,
            "prompts": prompts,
        }

    return {
        "status": "measured" if samples else "blocked",
        "blocked_reason": None if samples else "No API requests were attempted.",
        "summary": summarize(samples),
        "warmup_failures": warmup_failures,
        "samples": samples,
        "prompts": prompts,
    }


def measure_model(
    model_path: str | None,
    runs: int,
    warmup: int,
    max_new_tokens: int,
    timeout: float,
) -> tuple[dict, float | None]:
    from inference.adapter import InferenceAdapter
    from inference.exceptions import InferenceError

    model_load_started = time.perf_counter()
    try:
        adapter = InferenceAdapter(model_path=model_path)
    except InferenceError as exc:
        return ({
            "status": "blocked",
            "blocked_reason": f"{type(exc).__name__}: {exc}",
            "warmup_failures": [],
            "samples": [],
            "summary": summarize([]),
        }, round(time.perf_counter() - model_load_started, 3))
    model_load_seconds = time.perf_counter() - model_load_started

    if not adapter.is_loaded:
        return ({
            "status": "blocked",
            "blocked_reason": (
                "ModelNotReadyError: adapter did not load a model; configure "
                "LLM_MODEL_PATH or pass --model-path."
            ),
            "warmup_failures": [],
            "samples": [],
            "summary": summarize([]),
        }, round(model_load_seconds, 3))

    warmup_failures = []
    for prompt_index, prompt in enumerate(PROMPTS, start=1):
        for warmup_index in range(1, warmup + 1):
            try:
                adapter.generate(
                    prompt=prompt,
                    max_new_tokens=max_new_tokens,
                    timeout_sec=timeout,
                )
            except InferenceError as exc:
                warmup_failures.append({
                    "prompt_index": prompt_index,
                    "warmup_index": warmup_index,
                    "error": f"{type(exc).__name__}: {exc}",
                })
                return ({
                    "status": "blocked",
                    "blocked_reason": warmup_failures[-1]["error"],
                    "warmup_failures": warmup_failures,
                    "samples": [],
                    "summary": summarize([]),
                }, round(model_load_seconds, 3))

    samples = []
    for prompt_index, prompt in enumerate(PROMPTS, start=1):
        for run_index in range(1, runs + 1):
            started = time.perf_counter()
            try:
                adapter.generate(
                    prompt=prompt,
                    max_new_tokens=max_new_tokens,
                    timeout_sec=timeout,
                )
                error = None
                status = "success"
            except InferenceError as exc:
                error = f"{type(exc).__name__}: {exc}"
                status = "failure"
            elapsed_ms = (time.perf_counter() - started) * 1000
            samples.append({
                "prompt_index": prompt_index,
                "run_index": run_index,
                "status": status,
                "latency_ms": round(elapsed_ms, 3),
                "error": error,
            })

    return ({
        "status": "measured",
        "blocked_reason": None,
        "warmup_failures": warmup_failures,
        "samples": samples,
        "summary": summarize(samples),
    }, round(model_load_seconds, 3))


def _positive_int(value: str) -> int:
    parsed = int(value)
    if parsed < 1:
        raise argparse.ArgumentTypeError("must be at least 1")
    return parsed


def _nonnegative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be zero or greater")
    return parsed


def _positive_float(value: str) -> float:
    parsed = float(value)
    if parsed <= 0:
        raise argparse.ArgumentTypeError("must be greater than zero")
    return parsed


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--runs", type=_positive_int, default=3, help="measured runs per prompt")
    parser.add_argument("--warmup", type=_nonnegative_int, default=1, help="warm-up runs per prompt and stage")
    parser.add_argument("--timeout", type=_positive_float, default=20.0, help="HTTP and model timeout in seconds")
    parser.add_argument("--max-new-tokens", type=_positive_int, default=64)
    parser.add_argument("--model-path", help="GGUF model path; defaults to LLM_MODEL_PATH")
    parser.add_argument("--output", type=Path, help="JSON report path")
    args = parser.parse_args()

    model_path = args.model_path or os.getenv("LLM_MODEL_PATH")
    result = {
        "schema_version": 1,
        "run_id": str(uuid4()),
        "started_at_utc": datetime.now(timezone.utc).isoformat(),
        "configuration": {
            "api_base_url": args.base_url,
            "runs_per_prompt": args.runs,
            "warmup_runs_per_prompt": args.warmup,
            "prompt_set": list(PROMPTS),
            "http_timeout_seconds": args.timeout,
            "model_timeout_seconds": args.timeout,
            "max_new_tokens": args.max_new_tokens,
            "ttft": {
                "status": "not_applicable",
                "reason": "The adapter makes non-streaming generation calls.",
            },
        },
        "environment": environment(model_path),
    }
    result["environment"]["generation"].update({
        "max_new_tokens": args.max_new_tokens,
        "timeout_seconds": args.timeout,
        "warmup_per_prompt": args.warmup,
        "measured_runs_per_prompt": args.runs,
    })

    print("Measuring live API round-trip latency...")
    result["api_round_trip"] = measure_api(
        args.base_url,
        args.runs,
        args.warmup,
        args.timeout,
    )
    print("Measuring direct adapter generation latency...")
    model_result, model_load_seconds = measure_model(
        model_path,
        args.runs,
        args.warmup,
        args.max_new_tokens,
        args.timeout,
    )
    model_result["model_load_seconds_excluded_from_generation"] = model_load_seconds
    result["model_generation"] = model_result
    result["finished_at_utc"] = datetime.now(timezone.utc).isoformat()

    output = args.output or ROOT / "results" / f"demo-benchmark-{result['run_id']}.json"
    output = output if output.is_absolute() else ROOT / output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"Report written to {output}")
    print(
        "API: "
        f"{result['api_round_trip']['summary']['successes']} success / "
        f"{result['api_round_trip']['summary']['failures']} failed; "
        f"median={result['api_round_trip']['summary']['latency_ms']['median']} ms"
    )
    print(
        "Model: "
        f"{model_result['summary']['successes']} success / "
        f"{model_result['summary']['failures']} failed; "
        f"median={model_result['summary']['latency_ms']['median']} ms; "
        f"status={model_result['status']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
