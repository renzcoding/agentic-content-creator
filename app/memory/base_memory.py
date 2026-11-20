from abc import ABC, abstractmethod


class BaseMemory(ABC):
    """Define the standard interface for agent memory systems."""

    @abstractmethod
    def save(self, key: str, value: str) -> None:
        """Store a memory value using the given key."""
        raise NotImplementedError

    @abstractmethod
    def retrieve(self, key: str) -> str | None:
        """Retrieve a memory value by its key."""
        raise NotImplementedError

    @abstractmethod
    def clear(self) -> None:
        """Remove all stored memories."""
        raise NotImplementedError
