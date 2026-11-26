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
    def test_rejects_invalid_json_response(self, mock_urlopen):
        """Reject responses that cannot be decoded as JSON."""
        mock_urlopen.return_value = BytesIO(b"invalid json")

        with self.assertRaisesRegex(ValueError, "invalid JSON"):
            generate_response("Test prompt")

    @patch("app.services.ollama_service.urlopen")
    def test_rejects_non_object_json_response(self, mock_urlopen):
        """Reject JSON responses that are not objects."""
        mock_urlopen.return_value = BytesIO(b'["unexpected"]')

        with self.assertRaisesRegex(ValueError, "JSON object"):
            generate_response("Test prompt")

    @patch("app.services.ollama_service.urlopen")
    def test_rejects_missing_response_field(self, mock_urlopen):
        """Reject JSON responses without a response field."""
        mock_urlopen.return_value = BytesIO(b'{"model": "qwen2.5:0.5b"}')

        with self.assertRaisesRegex(ValueError, "non-empty text"):
            generate_response("Test prompt")

    @patch("app.services.ollama_service.urlopen")
    def test_rejects_non_string_response(self, mock_urlopen):
        """Reject generated responses that are not strings."""
        mock_urlopen.return_value = BytesIO(b'{"response": 123}')

        with self.assertRaisesRegex(ValueError, "non-empty text"):
            generate_response("Test prompt")

    @patch("app.services.ollama_service.urlopen")
    def test_rejects_empty_generated_response(self, mock_urlopen):
        """Reject generated responses containing only whitespace."""
        mock_urlopen.return_value = BytesIO(b'{"response": "   "}')

        with self.assertRaisesRegex(ValueError, "non-empty text"):
            generate_response("Test prompt")


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
