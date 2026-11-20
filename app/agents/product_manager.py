from app.agents.base_agent import BaseAgent
from app.memory.base_memory import BaseMemory
from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.ollama_provider import OllamaProvider


class ProductManagerAgent(BaseAgent):
    """Translate product requests into structured requirements using an LLM."""

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
        memory: BaseMemory | None = None,
    ) -> None:
        """Initialize the agent with optional provider and memory."""
        super().__init__(
            name="Product Manager",
            role="Product planning and requirements",
            memory=memory,
        )
        self.provider = provider if provider is not None else OllamaProvider()

    def run(self, task: str) -> str:
        """Generate requirements using the task and available memory context."""
        if not task.strip():
            raise ValueError("Task must not be empty.")

        # Retrieve previously stored project context when available.
        context = self.recall("project_context") if self.memory else None
        context_section = (
            f"Previous Context: {context}\n\n" if context else ""
        )

        prompt = (
            "Act as a product manager. Be concise and follow the format exactly.\n"
            f"{context_section}"
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
