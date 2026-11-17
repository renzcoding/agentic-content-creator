import unittest
from unittest.mock import patch

from app.services.llm.ollama_provider import OllamaProvider


class TestOllamaProvider(unittest.TestCase):
    """Test the Ollama provider implementation."""

    def setUp(self):
        """Create an Ollama provider for each test."""
        self.provider = OllamaProvider()

    # Mock the Ollama service to isolate provider behavior during testing.
    @patch("app.services.llm.ollama_provider.generate_response")
    def test_generates_response(self, mock_generate):
        """Verify that prompts are forwarded to Ollama service."""
        # Simulate the response returned by the Ollama service.
        mock_generate.return_value = "Generated response"

        # Execute the provider with a sample prompt.
        result = self.provider.generate("Test prompt")

        self.assertEqual(result, "Generated response")
        mock_generate.assert_called_once_with("Test prompt")


if __name__ == "__main__":
    unittest.main()
