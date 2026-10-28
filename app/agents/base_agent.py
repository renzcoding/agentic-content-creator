from abc import ABC, abstractmethod


class BaseAgent(ABC):
    """Define the standard interface for all AI agents."""

    def __init__(self, name: str, role: str) -> None:
        """Initialize an agent with its name and responsibility."""
        self.name = name
        self.role = role

    @abstractmethod
    def run(self, task: str) -> str:
        """Execute a task and return the agent's result."""
        raise NotImplementedError
