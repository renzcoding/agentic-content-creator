from app.agents.base_agent import BaseAgent
from app.memory.base_memory import BaseMemory
from app.memory.conversation_memory import ConversationMemory
from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.ollama_provider import OllamaProvider


class ProductManagerAgent(BaseAgent):
    """Translate product requests into structured requirements using an LLM."""

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
        memory: BaseMemory | None = None,
        conversation_memory: ConversationMemory | None = None,
        history_limit: int = 5,
    ) -> None:
        """Initialize the agent with optional memory and LLM dependencies."""
        super().__init__(
            name="Product Manager",
            role="Product planning and requirements",
            memory=memory,
        )

        if history_limit < 1:
            raise ValueError("History limit must be greater than zero.")

        self.provider = provider if provider is not None else OllamaProvider()
        self.conversation_memory = conversation_memory
        self.history_limit = history_limit

    def run(self, task: str) -> str:
        """Generate requirements using project context and recent conversation."""
        if not task.strip():
            raise ValueError("Task must not be empty.")

        # Retrieve persistent project context when configured.
        context = self.recall("project_context") if self.memory else None

        # Retrieve recent conversation messages when configured.
        history = (
            self.conversation_memory.get_history(limit=self.history_limit)
            if self.conversation_memory
            else []
        )

        history_section = ""
        if history:
            history_lines = [
                f"{message['role']}: {message['content']}"
                for message in history
            ]
            history_section = (
                "Recent Conversation:\n"
                + "\n".join(history_lines)
                + "\n\n"
            )

        context_section = (
            f"Previous Context: {context}\n\n" if context else ""
        )

        prompt = (
            "Act as a product manager. Be concise and follow the format exactly.\n"
            f"{context_section}"
            f"{history_section}"
            f"Objective: {task.strip()}\n\n"
            "Return these four sections only:\n"
            "PRODUCT REQUIREMENTS\n"
            "Objective: One sentence.\n"
            "Scope: Three short bullet points.\n"
            "User Needs: Two short bullet points.\n"
            "Acceptance Criteria: Three numbered, testable criteria.\n"
            "Do not repeat headings. Do not end mid-sentence."
        )

        # Generate the response before updating conversation history.
        response = self.provider.generate(prompt)

        # Persist the current user request and assistant response.
        if self.conversation_memory:
            self.conversation_memory.add_message("user", task.strip())
            self.conversation_memory.add_message("assistant", response)

        return response
