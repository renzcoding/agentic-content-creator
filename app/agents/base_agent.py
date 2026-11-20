from abc import ABC, abstractmethod

from app.memory.base_memory import BaseMemory


class BaseAgent(ABC):
    """Define the standard interface for all AI agents."""

    def __init__(
        self,
        name: str,
        role: str,
        memory: BaseMemory | None = None,
    ) -> None:
        """Initialize agent identity and optional memory storage."""
        self.name = name
        self.role = role
        self.memory = memory

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
