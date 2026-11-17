from abc import ABC, abstractmethod


class BaseLLMProvider(ABC):
    """Define the standard interface for all LLM providers."""

    @abstractmethod
    def generate(self, prompt: str) -> str:
        """Generate text from a prompt using an LLM provider."""

        # Require concrete providers to implement this method.
        raise NotImplementedError