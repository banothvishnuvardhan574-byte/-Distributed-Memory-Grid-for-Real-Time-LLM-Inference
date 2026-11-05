"""
Unit and Contract Tests for Inference Adapter
Targeted for Sagar's test runner and CI verification.
"""

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
        """Verify worker handler catches ModelNotReadyError and returns failed schema."""
        job = {"request_id": "req-101", "prompt": "Hello world"}
        result = handle_worker_job(job)

        self.assertEqual(result["request_id"], "req-101")
        self.assertEqual(result["status"], "failed")
        self.assertIn("ModelUnavailable", result["error"])


if __name__ == "__main__":
    unittest.main()
