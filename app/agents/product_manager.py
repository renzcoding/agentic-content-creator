from config.settings import (
    PROJECT_CONTEXT_CHAR_LIMIT,
    PROMPT_TOKEN_BUDGET,
    RECENT_HISTORY_CHAR_LIMIT,
    RELEVANT_CONTEXT_CHAR_LIMIT,
    RELEVANT_CONTEXT_LIMIT,
)
from app.agents.base_agent import BaseAgent
from app.memory.base_memory import BaseMemory
from app.memory.conversation_memory import ConversationMemory
from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.ollama_provider import OllamaProvider
from app.utils.token_estimator import estimate_tokens


class ProductManagerAgent(BaseAgent):
    """Translate product requests into structured requirements using an LLM."""

    def __init__(
        self,
        provider: BaseLLMProvider | None = None,
        memory: BaseMemory | None = None,
        conversation_memory: ConversationMemory | None = None,
        history_limit: int = 5,
        session_id: str = "default",
        prompt_token_budget: int = PROMPT_TOKEN_BUDGET,
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

        if not session_id.strip():
            raise ValueError("Session ID must not be empty.")
        self.session_id = session_id.strip()
        if prompt_token_budget < 1:
            raise ValueError("Prompt token budget must be greater than zero.")
        self.prompt_token_budget = prompt_token_budget
        self.last_prompt_token_estimate = 0

    @staticmethod
    def _limit_text(text: str, max_chars: int) -> str:
        """Trim text to a character budget without exceeding the limit."""
        return text[:max_chars]


    @staticmethod
    def _format_messages(
        messages: list[dict[str, str]],
        max_chars: int,
    ) -> str:
        """Format messages while keeping the total output within its budget."""
        if max_chars <= 0:
            return ""

        lines = []
        remaining = max_chars

        for message in messages:
            line = f"{message['role']}: {message['content']}"
            separator = 1 if lines else 0
            available = remaining - separator

            if available <= 0:
                break

            lines.append(line[:available])
            remaining -= separator + min(len(line), available)

            if len(line) > available:
                break

        return "\n".join(lines)


    def _fit_prompt_to_budget(
        self,
        prompt: str,
        task: str,
        context: str | None,
        history: list[dict[str, str]],
        relevant_messages: list[dict[str, str]],
    ) -> str:
        """Reduce optional context until the prompt fits the token budget."""

        # Copy context collections to avoid modifying the original data.
        history = history.copy()
        relevant_messages = relevant_messages.copy()

        # Preserve required instructions and the current user objective.
        while estimate_tokens(prompt) > self.prompt_token_budget:
            if relevant_messages:
                relevant_messages.pop()
            elif history:
                history.pop(0)
            elif context:
                context = None
            else:
                raise ValueError(
                    "Required prompt content exceeds the token budget."
                )

            # Rebuild the prompt after reducing optional context.
            prompt = self._build_prompt(
                task,
                context,
                history,
                relevant_messages,
            )

        return prompt


    def _build_prompt(
        self,
        task: str,
        context: str | None,
        history: list[dict[str, str]],
        relevant_messages: list[dict[str, str]],
    ) -> str:
        """Build the LLM prompt from required instructions and optional context."""

        # Format recent conversation history within its character budget.
        history_section = ""
        if history:
            history_text = self._format_messages(
                history,
                RECENT_HISTORY_CHAR_LIMIT,
            )
            if history_text:
                history_section = f"Recent Conversation:\n{history_text}\n\n"

        # Format relevant older messages within their character budget.
        relevant_section = ""
        if relevant_messages:
            relevant_text = self._format_messages(
                relevant_messages,
                RELEVANT_CONTEXT_CHAR_LIMIT,
            )
            if relevant_text:
                relevant_section = (
                    f"Relevant Previous Conversation:\n{relevant_text}\n\n"
                )

        # Include persistent project context when available.
        context_section = (
            f"Previous Context: {context}\n\n" if context else ""
        )

        # Keep system instructions and the current objective in the prompt.
        return (
            "Act as a product manager. Be concise and follow the format exactly.\n"
            f"{context_section}"
            f"{history_section}"
            f"{relevant_section}"
            f"Objective: {task.strip()}\n\n"
            "Return these four sections only:\n"
            "PRODUCT REQUIREMENTS\n"
            "Objective: One sentence.\n"
            "Scope: Three short bullet points.\n"
            "User Needs: Two short bullet points.\n"
            "Acceptance Criteria: Three numbered, testable criteria.\n"
            "Do not repeat headings. Do not end mid-sentence."
        )

    def run(self, task: str) -> str:
        """Generate requirements using project context and relevant conversation."""
        if not task.strip():
            raise ValueError("Task must not be empty.")

        # Retrieve persistent project context when configured.
        context = self.recall("project_context") if self.memory else None
        if context:
            context = self._limit_text(
                context,
                PROJECT_CONTEXT_CHAR_LIMIT,
            )

        # Retrieve messages from the current conversation session.
        all_messages = (
            self.conversation_memory.get_history(
                session_id=self.session_id,
            )
            if self.conversation_memory
            else []
        )

        # Keep only the configured number of recent messages.
        history = all_messages[-self.history_limit:]

        # Search older messages using meaningful task keywords.
        relevant_messages = []
        if self.conversation_memory:
            keywords = {
                word.strip(".,!?;:()[]{}\"'").casefold()
                for word in task.split()
                if len(word.strip(".,!?;:()[]{}\"'")) >= 3
            }

            if keywords:
                matches = self.conversation_memory.search_messages(
                    keyword=sorted(keywords),
                    session_id=self.session_id,
                )

                recent_keys = {
                    (message["role"], message["content"])
                    for message in history
                }
                relevant_messages = [
                    message
                    for message in matches
                    if (message["role"], message["content"]) not in recent_keys
                ][:RELEVANT_CONTEXT_LIMIT]

        # Build the initial prompt with all available context.
        prompt = self._build_prompt(
            task,
            context,
            history,
            relevant_messages,
        )

        # Reduce optional context until the prompt fits the token budget.
        prompt = self._fit_prompt_to_budget(
            prompt,
            task,
            context,
            history,
            relevant_messages,
        )

        # Store the final prompt token estimate before provider generation.
        self.last_prompt_token_estimate = estimate_tokens(prompt)

        # Generate the response before updating conversation history.
        response = self.provider.generate(prompt)

        # Persist the current user request and assistant response.
        if self.conversation_memory:
            self.conversation_memory.add_message(
                "user", task.strip(), self.session_id
            )
            self.conversation_memory.add_message(
                "assistant", response, self.session_id
            )

        return response
