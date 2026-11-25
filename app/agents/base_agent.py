from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from app.memory.base_memory import BaseMemory


class BaseAgent(ABC):
    """Define the standard interface for all AI agents."""

    def __init__(
        self,
        name: str,
        role: str,
        memory: BaseMemory | None = None,
        agent_id: str | None = None,
        formal_name: str | None = None,
        division_id: str | None = None,
        manager_agent_id: str | None = None,
    ) -> None:
        """Initialize permanent identity and optional organizational metadata."""
        # Reject missing or whitespace-only identity fields.
        if not name.strip():
            raise ValueError("Agent name must not be empty.")

        if not role.strip():
            raise ValueError("Agent role must not be empty.")

        self.name = name.strip()
        self.role = role.strip()
        self.memory = memory

        # Generate a permanent UUID v4 or restore an existing valid identity.
        parsed_agent_id = UUID(agent_id) if agent_id is not None else uuid4()

        if parsed_agent_id.version != 4:
            raise ValueError("Agent ID must be a valid UUID version 4.")

        self._agent_id = str(parsed_agent_id)

        # Store optional organizational metadata without requiring registration.
        self.formal_name = formal_name
        self.division_id = division_id
        self.manager_agent_id = manager_agent_id

    @property
    def agent_id(self) -> str:
        """Return the permanent, read-only agent identifier."""
        return self._agent_id

    def remember(self, key: str, value: str) -> None:
        """Store information using an agent-specific memory key."""
        if self.memory is None:
            raise RuntimeError("Memory is not configured for this agent.")

        memory_key = f"{self.name}:{key}"
        self.memory.save(memory_key, value)

    def recall(self, key: str) -> str | None:
        """Retrieve information using an agent-specific memory key."""
        if self.memory is None:
            raise RuntimeError("Memory is not configured for this agent.")

        memory_key = f"{self.name}:{key}"
        return self.memory.retrieve(memory_key)

    @abstractmethod
    def run(self, task: str) -> str:
        """Execute a task and return the agent's result."""
        raise NotImplementedError
