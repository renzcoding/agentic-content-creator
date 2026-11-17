from app.agents.base_agent import BaseAgent
from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.ollama_provider import OllamaProvider


class ProductManagerAgent(BaseAgent):
    """Translate product requests into structured requirements using an LLM."""

    def __init__(self, provider: BaseLLMProvider | None = None) -> None:
        """Initialize the agent with an injected LLM provider."""
        super().__init__(
            name="Product Manager",
            role="Product planning and requirements",
        )
        self.provider = provider if provider is not None else OllamaProvider()

    def run(self, task: str) -> str:
        """Generate a concise and structured requirements brief."""
        if not task.strip():
            raise ValueError("Task must not be empty.")

        prompt = (
            "Act as a product manager. Be concise and follow the format exactly.\n"
            f"Objective: {task.strip()}\n\n"
            "Return these four sections only:\n"
            "PRODUCT REQUIREMENTS\n"
            "Objective: One sentence.\n"
            "Scope: Three short bullet points.\n"
            "User Needs: Two short bullet points.\n"
            "Acceptance Criteria: Three numbered, testable criteria.\n"
            "Do not repeat headings. Do not end mid-sentence."
        )

        return self.provider.generate(prompt)
