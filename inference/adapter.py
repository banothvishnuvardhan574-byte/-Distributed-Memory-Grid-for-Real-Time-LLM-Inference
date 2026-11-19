import os
import time
import logging
import json
from urllib import request as urllib_request
from urllib.error import URLError
from pathlib import Path
from typing import Optional, Dict, Any

from inference.exceptions import (
    InferenceError,
    ModelNotReadyError,
    InferenceTimeoutError,
    InvalidPromptError,
)

logger = logging.getLogger("inference_adapter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")

 feat/recent-prompt-history-pagination
_AUTO_CONFIGURE = object()


DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "models",
    "qwen2.5-0.5b-instruct-q4_k_m.gguf"
)
 main

class InferenceAdapter:
    _instance: Optional["InferenceAdapter"] = None

 feat/recent-prompt-history-pagination
    def __init__(self, model_path: Optional[str] | object = _AUTO_CONFIGURE, n_threads: int = 2):
        if model_path is _AUTO_CONFIGURE:
            configured_path = os.getenv("LLM_MODEL_PATH")
        else:
            configured_path = model_path

        if configured_path:
            self.model_path = configured_path
        else:
            if model_path is _AUTO_CONFIGURE:
                model_dir = Path(__file__).resolve().parent.parent / "models"
                candidates = sorted(model_dir.glob("*.gguf"))
                self.model_path = str(candidates[0]) if candidates else None
            else:
                self.model_path = None
                
    def __init__(self, model_path: Optional[str] = None, n_threads: int = 2):
        self.model_path = model_path or os.getenv("LLM_MODEL_PATH", DEFAULT_MODEL_PATH)
 main
        self.n_threads = n_threads
        self.is_loaded = False
        self._model = None
        self._inference_backend = "llama"
        self._ollama_model = os.getenv("OLLAMA_MODEL", "qwen2.5:0.5b")
        self._ollama_url = os.getenv("OLLAMA_URL", "http://127.0.0.1:11434")
        self.model_metadata: Dict[str, Any] = {
            "model_name": "Qwen2.5-0.5B-Instruct",
            "format": "GGUF Q4_K_M",
            "device": "CPU",
            "threads": self.n_threads,
        }

        if self.model_path and os.path.exists(self.model_path):
            self._load_model()
        else:
            logger.warning(
                f"Model file not found at '{self.model_path}'. "
                "Adapter ready in uninitialized state."
            )

    @classmethod
 feat/recent-prompt-history-pagination
    def get_instance(cls, model_path: Optional[str] | object = _AUTO_CONFIGURE) -> "InferenceAdapter":
        """Singleton accessor to ensure weights stay cached in memory."""

    def get_instance(cls, model_path: Optional[str] = None) -> "InferenceAdapter":
 main
        if cls._instance is None:
            cls._instance = cls(model_path=model_path)
        return cls._instance

    def _load_model(self) -> None:
 feat/recent-prompt-history-pagination
        """Load a local GGUF with llama.cpp, with Ollama as a fallback runtime."""
        start_time = time.time()
        llama_error = None

        if self.model_path:
            logger.info(f"Loading weights from {self.model_path} onto CPU...")
            try:
                from llama_cpp import Llama
                self._model = Llama(
                    model_path=self.model_path,
                    n_threads=self.n_threads,
                    n_ctx=1024,
                    verbose=False,
                )
                self._inference_backend = "llama"
                self.is_loaded = True
                load_duration = time.time() - start_time
                logger.info(f"Model loaded successfully in {load_duration:.2f}s.")
                self.model_metadata["load_time_sec"] = round(load_duration, 3)
                return
            except Exception as exc:
                llama_error = exc
                logger.warning("llama.cpp runtime unavailable: %s", exc)

        try:
            with urllib_request.urlopen(
                f"{self._ollama_url}/api/tags",
                timeout=3,
            ) as response:
                tags = json.loads(response.read().decode("utf-8"))

            available_models = {
                item.get("name")
                for item in tags.get("models", [])
                if item.get("name")
            }
            if (
                self._ollama_model not in available_models
                and f"{self._ollama_model}:latest" not in available_models
            ):
                raise ModelNotReadyError(
                    f"Ollama model '{self._ollama_model}' is not installed. "
                    f"Run: ollama pull {self._ollama_model}"
                )

            self._model = "ollama"
            self._inference_backend = "ollama"

        start_time = time.time()
        logger.info(f"Loading weights from {self.model_path} onto CPU...")
        try:
            from llama_cpp import Llama
            self._model = Llama(
                model_path=self.model_path,
                n_threads=self.n_threads,
                n_ctx=1024,
                verbose=False,
            )
 main
            self.is_loaded = True
            load_duration = time.time() - start_time
            logger.info(
                "Ollama model %s ready in %.2fs.",
                self._ollama_model,
                load_duration,
            )
            self.model_metadata["load_time_sec"] = round(load_duration, 3)
 feat/recent-prompt-history-pagination
            return
        except ModelNotReadyError:
            raise
        except (URLError, TimeoutError, json.JSONDecodeError, OSError) as exc:
            detail = str(llama_error or exc)
            raise ModelNotReadyError(
                f"Model runtime is unavailable. llama.cpp error: {detail}"
            ) from exc

        except Exception as e:
            self.is_loaded = False
            self._model = None
            raise ModelNotReadyError(f"Failed to load model weights: {str(e)}") from e
 main

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 64,
        timeout_sec: float = 15.0,
        temperature: float = 0.7,
    ) -> str:
        if prompt is None or not isinstance(prompt, str) or not prompt.strip():
            raise InvalidPromptError("Prompt must be a non-empty string.")

        if not self.is_loaded or self._model is None:
            raise ModelNotReadyError(
                "Model runtime is uninitialized. Weights must be loaded before inference."
            )

        start_time = time.time()
        logger.info(f"Generating inference for prompt (chars={len(prompt)}, max_tokens={max_new_tokens})...")

        try:
            output = self._model(
                prompt,
                max_tokens=max_new_tokens,
                temperature=temperature,
                stop=["</s>", "<|im_end|>", "\n\nUser:"],
            )
            elapsed = time.time() - start_time
            if elapsed > timeout_sec:
                raise InferenceTimeoutError(
                    f"Inference latency ({elapsed:.2f}s) exceeded budget ({timeout_sec:.2f}s)."
                )

            if not generated_text:
                raise InferenceError("Model returned empty generation output.")

            logger.info(f"Inference complete in {elapsed:.2f}s.")
            return generated_text

        except Exception as e:
            elapsed = time.time() - start_time
            if elapsed > timeout_sec:
                raise InferenceTimeoutError(f"Inference timeout after {elapsed:.2f}s.") from e
            if isinstance(e, InferenceError):
                raise
            raise InferenceError(f"Generation failure: {str(e)}") from e


_adapter_singleton: Optional[InferenceAdapter] = None

def get_adapter() -> InferenceAdapter:
    global _adapter_singleton
    if _adapter_singleton is None:
        _adapter_singleton = InferenceAdapter.get_instance()
    return _adapter_singleton

def generate_response(prompt: str, max_tokens: int = 64, timeout_sec: float = 15.0) -> str:
    adapter = get_adapter()
    return adapter.generate(prompt=prompt, max_new_tokens=max_tokens, timeout_sec=timeout_sec)
