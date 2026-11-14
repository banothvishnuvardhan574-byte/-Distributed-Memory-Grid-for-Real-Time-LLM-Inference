import time
import unittest
from unittest.mock import MagicMock, patch

from inference import (
    InferenceAdapter,
    InvalidPromptError,
    ModelNotReadyError,
    InferenceTimeoutError,
)
from examples.worker_integration_example import handle_worker_job


class TestInferenceAdapter(unittest.TestCase):

    def setUp(self):
        # Use an explicit non-existent path so unit tests stay isolated from local weights
        self.adapter = InferenceAdapter(model_path="models/non_existent_test_model.gguf")

    def test_empty_prompt_validation(self):
        """Empty or whitespace prompts must raise InvalidPromptError."""
        with self.assertRaises(InvalidPromptError):
            self.adapter.generate(prompt="")

        with self.assertRaises(InvalidPromptError):
            self.adapter.generate(prompt="   ")

        with self.assertRaises(InvalidPromptError):
            self.adapter.generate(prompt=None)

    def test_uninitialized_model_raises_model_not_ready(self):
        """Adapter must not return mock/stub text if weights are missing."""
        self.assertFalse(self.adapter.is_loaded)
        with self.assertRaises(ModelNotReadyError):
            self.adapter.generate(prompt="Explain distributed inference")

    def test_timeout_handling(self):
        """Simulated long-running inference must trigger InferenceTimeoutError."""
        self.adapter.is_loaded = True
        mock_model = MagicMock()

        def slow_inference(*args, **kwargs):
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

    @patch("examples.worker_integration_example.generate_response")
    def test_worker_handler_schema_compliance(self, mock_generate):
        """Verify worker handler catches ModelNotReadyError and returns failed schema."""
        mock_generate.side_effect = ModelNotReadyError("Weights missing")
        job = {"request_id": "req-101", "prompt": "Hello world"}
        result = handle_worker_job(job)

        self.assertEqual(result["request_id"], "req-101")
        self.assertEqual(result["status"], "failed")
        self.assertIn("Weights missing", result["error"])


if __name__ == "__main__":
    unittest.main()
