import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from config.settings import OLLAMA_MODEL


# Define the local Ollama API endpoint.
OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_response(prompt: str) -> str:
    """Send a prompt to Ollama and validate the generated response."""

    # Validate the prompt before making an HTTP request.
    if not isinstance(prompt, str) or not prompt.strip():
        raise ValueError("Prompt must be a non-empty string.")

    # Prepare the request payload for Ollama.
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"num_predict": 160},
    }).encode("utf-8")

    # Build an HTTP POST request with JSON content.
    request = Request(
        OLLAMA_URL,
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST",
    )

    try:
        # Send the request and wait for the model response.
        with urlopen(request, timeout=120) as response:
            raw_response = response.read().decode("utf-8")

    # Convert network and response decoding errors into application errors.
    except (URLError, TimeoutError, UnicodeDecodeError) as error:
        raise RuntimeError(f"Ollama request failed: {error}") from error

    try:
        # Decode the API response as JSON.
        result = json.loads(raw_response)
    except json.JSONDecodeError as error:
        raise ValueError("Ollama returned invalid JSON.") from error

    # Ensure the API response has the expected structure.
    if not isinstance(result, dict):
        raise ValueError("Ollama response must be a JSON object.")

    generated_text = result.get("response")

    # Reject missing, non-string, or empty generated text.
    if not isinstance(generated_text, str) or not generated_text.strip():
        raise ValueError("Ollama response must contain non-empty text.")

    return generated_text.strip()
