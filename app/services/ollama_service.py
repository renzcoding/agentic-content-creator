import json
from urllib.error import URLError
from urllib.request import Request, urlopen

from config.settings import OLLAMA_MODEL


# Define the local Ollama API endpoint.
OLLAMA_URL = "http://localhost:11434/api/generate"


def generate_response(prompt: str) -> str:
    """Send a prompt to Ollama and return the generated response."""

    # Reject empty prompts before making an HTTP request.
    if not prompt.strip():
        raise ValueError("Prompt must not be empty.")

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
            result = json.loads(response.read().decode("utf-8"))

    # Convert network errors into readable application errors.
    except (URLError, TimeoutError) as error:
        raise RuntimeError(f"Ollama request failed: {error}") from error

    # Return the generated text without surrounding whitespace.
    return result["response"].strip()