import json
import unittest
from io import BytesIO
from unittest.mock import patch
from urllib.error import URLError

from app.services.ollama_service import generate_response


class TestOllamaService(unittest.TestCase):
    """Test Ollama integration without requiring a running model."""

    def test_rejects_empty_prompt(self):
        """Ensure empty prompts are rejected."""
        with self.assertRaises(ValueError):
            generate_response(" ")

    # Mock the HTTP request to avoid requiring a running Ollama server.
    @patch("app.services.ollama_service.urlopen")
    def test_returns_generated_response(self, mock_urlopen):
        """Ensure generated text is extracted and trimmed."""
        # Simulate the JSON response returned by the Ollama API.
        response_data = json.dumps({
            "response": "  Ollama is working.  "
        }).encode("utf-8")
        mock_urlopen.return_value = BytesIO(response_data)

        result = generate_response("Test prompt")

        self.assertEqual(result, "Ollama is working.")
        mock_urlopen.assert_called_once()

    @patch("app.services.ollama_service.urlopen")
    def test_handles_connection_error(self, mock_urlopen):
        """Ensure connection errors become readable runtime errors."""
        # Simulate a network connection failure.
        mock_urlopen.side_effect = URLError("Connection failed")

        with self.assertRaisesRegex(RuntimeError, "Ollama request failed"):
            # Execute the service using the mocked HTTP response.
            generate_response("Test prompt")


if __name__ == "__main__":
    unittest.main()
