"""
LLM MemoryGrid — Inference Adapter
Owner: Suraj Kotrange (suraj-inference)
Contract Hand-off: generate_response(prompt: str) -> str
"""

import os
import sys
import time
import logging
from typing import Optional, Dict, Any

from inference.exceptions import (
    InferenceError,
    ModelNotReadyError,
    InferenceTimeoutError,
    InvalidPromptError,
)

logger = logging.getLogger("inference_adapter")
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")


class InferenceAdapter:
    """
    Encapsulates local LLM loading and bounded text generation.
    Maintains a persistent instance to prevent reloading model weights per request.
    """

    _instance: Optional["InferenceAdapter"] = None

    def __init__(self, model_path: Optional[str] = None, n_threads: int = 2):
        self.model_path = model_path or os.getenv("LLM_MODEL_PATH")
        self.n_threads = n_threads
        self.is_loaded = False
        self._model = None
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
                "Adapter ready in uninitialized state. Call load_model() with valid path."
            )

    @classmethod
    def get_instance(cls, model_path: Optional[str] = None) -> "InferenceAdapter":
        """Singleton accessor to ensure weights stay cached in memory."""
        if cls._instance is None:
            cls._instance = cls(model_path=model_path)
        return cls._instance

    def _load_model(self) -> None:
        """Internal loader using llama_cpp or runtime fallback."""
        start_time = time.time()
        logger.info(f"Loading weights from {self.model_path} onto CPU...")
        try:
            # Check for llama-cpp-python
            try:
                from llama_cpp import Llama
                self._model = Llama(
                    model_path=self.model_path,
                    n_threads=self.n_threads,
                    n_ctx=1024,
                    verbose=False,
                )
                self.is_loaded = True
            except ImportError:
                # If llama-cpp not installed, check if ONNX / fallback model exists
                logger.error("llama-cpp-python is not installed in the active environment.")
                raise ModelNotReadyError(
                    "llama-cpp-python runtime is not installed. Run: pip install llama-cpp-python"
                )

            load_duration = time.time() - start_time
            logger.info(f"Model loaded successfully in {load_duration:.2f}s.")
            self.model_metadata["load_time_sec"] = round(load_duration, 3)

        except Exception as e:
            self.is_loaded = False
            self._model = None
            if not isinstance(e, InferenceError):
                raise ModelNotReadyError(f"Failed to load model weights: {str(e)}") from e
            raise

    def generate(
        self,
        prompt: str,
        max_new_tokens: int = 128,
        timeout_sec: float = 15.0,
        temperature: float = 0.7,
    ) -> str:
        """
        Executes bounded text inference.
        Enforces timeout, input validation, and genuine completion.
        """
        if prompt is None or not isinstance(prompt, str) or not prompt.strip():
            raise InvalidPromptError("Prompt must be a non-empty string.")

        if not self.is_loaded or self._model is None:
            raise ModelNotReadyError(
                "Model runtime is uninitialized. Weights must be loaded before inference."
            )

        start_time = time.time()
        logger.info(f"Generating inference for prompt (chars={len(prompt)}, max_tokens={max_new_tokens})...")

        try:
            # Llama-cpp invocation
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

            generated_text = output["choices"][0]["text"].strip()
            if not generated_text:
                raise InferenceError("Model returned empty generation output.")

            logger.info(f"Inference complete in {elapsed:.2f}s.")
            return generated_text

        except Exception as e:
            elapsed = time.time() - start_time
            if elapsed > timeout_sec:
                raise InferenceTimeoutError(
                    f"Inference timeout after {elapsed:.2f}s."
                ) from e
            if isinstance(e, InferenceError):
                raise
            raise InferenceError(f"Generation failure during execution: {str(e)}") from e


# Public Top-Level API Contract agreed with Vishnu and Nikhila
_adapter_singleton: Optional[InferenceAdapter] = None

def get_adapter() -> InferenceAdapter:
    global _adapter_singleton
    if _adapter_singleton is None:
        _adapter_singleton = InferenceAdapter.get_instance()
    return _adapter_singleton

def generate_response(prompt: str, max_tokens: int = 128, timeout_sec: float = 15.0) -> str:
    """
    Public API contract for Nikhila's worker handler and Vishnu's backend.
    
    Args:
        prompt: User input string.
        max_tokens: Upper ceiling for generated tokens (default: 128).
        timeout_sec: Maximum latency budget in seconds (default: 15.0).
        
    Returns:
        Generated response string.
        
    Raises:
        InvalidPromptError: If prompt is empty or malformed.
        ModelNotReadyError: If model weights are not loaded.
        InferenceTimeoutError: If execution exceeds timeout budget.
        InferenceError: For internal runtime errors.
    """
    adapter = get_adapter()
    return adapter.generate(prompt=prompt, max_new_tokens=max_tokens, timeout_sec=timeout_sec)
