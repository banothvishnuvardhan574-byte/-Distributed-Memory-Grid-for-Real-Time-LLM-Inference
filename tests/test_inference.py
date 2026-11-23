"""
Unit and Contract Tests for Inference Adapter
Targeted for Sagar's test runner and CI verification.
"""

import builtins
import unittest
from unittest.mock import MagicMock, patch

from inference import (
    InferenceAdapter,
    generate_response,
    InvalidPromptError,
    ModelNotReadyError,
    InferenceTimeoutError,
    InferenceError,
)
from examples.worker_integration_example import handle_worker_job


class TestInferenceAdapter(unittest.TestCase):

    def setUp(self):
        # Reset adapter instance for testing
        self.adapter = InferenceAdapter(model_path=None)

    def test_empty_prompt_validation(self):
        """Empty or whitespace prompts must raise InvalidPromptError."""
        with self.assertRaises(InvalidPromptError):
            self.adapter.generate(prompt="")

        with self.assertRaises(InvalidPromptError):
            self.adapter.generate(prompt="   ")

        with self.assertRaises(InvalidPromptError):
            self.adapter.generate(prompt=None)

    def test_uninitialized_model_raises_model_not_ready(self):
        """Adapter must not return mock/stub text if weights are uninitialized."""
        self.assertFalse(self.adapter.is_loaded)
        with self.assertRaises(ModelNotReadyError):
            self.adapter.generate(prompt="Explain distributed inference")

    def test_available_ollama_model_is_preferred_over_llama_cpp(self):
        response = MagicMock()
        response.__enter__.return_value.read.return_value = (
            b'{"models":[{"name":"qwen2.5:0.5b"}]}'
        )
        self.adapter.model_path = "local-model.gguf"

        with (
            patch(
                "inference.adapter.urllib_request.urlopen",
                return_value=response,
            ),
            patch("builtins.__import__", wraps=builtins.__import__) as importer,
        ):
            self.adapter._load_model()

        self.assertTrue(self.adapter.is_loaded)
        self.assertEqual(self.adapter._inference_backend, "ollama")
        self.assertFalse(
            any(call.args[0] == "llama_cpp" for call in importer.call_args_list)
        )

    def test_timeout_handling(self):
        """Simulated long-running inference must trigger InferenceTimeoutError."""
        self.adapter.is_loaded = True
        mock_model = MagicMock()
        def slow_inference(*args, **kwargs):
            import time
            time.sleep(0.15)
            return {"choices": [{"text": "delayed output"}]}
        mock_model.side_effect = slow_inference
        self.adapter._model = mock_model

        with self.assertRaises(InferenceTimeoutError):
            self.adapter.generate(prompt="Test prompt", timeout_sec=0.05)

    def test_successful_mocked_llm_inference(self):
        """When backend generates text, adapter formats and returns string."""
        self.adapter.is_loaded = True
        mock_model = MagicMock()
        mock_model.return_value = {"choices": [{"text": " Distributed inference shards computation."}]}
        self.adapter._model = mock_model

        result = self.adapter.generate(prompt="What is distributed inference?", max_new_tokens=32)
        self.assertEqual(result, "Distributed inference shards computation.")

    def test_worker_handler_schema_compliance(self):
        """Verify worker handler returns a schema-compliant inference response."""
        job = {"request_id": "req-101", "prompt": "Hello world"}
        result = handle_worker_job(job)

        self.assertEqual(result["request_id"], "req-101")
        self.assertEqual(result["status"], "completed")
        self.assertIsInstance(result["response"], str)


if __name__ == "__main__":
    unittest.main()
