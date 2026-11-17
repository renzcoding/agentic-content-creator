from app.services.llm.base_provider import BaseLLMProvider
from app.services.ollama_service import generate_response


class OllamaProvider(BaseLLMProvider):
    """Provide local LLM generation through Ollama."""

    def generate(self, prompt: str) -> str:
        """Generate text using the configured local Ollama model."""

        # Delegate text generation to the Ollama service.
        return generate_response(prompt)