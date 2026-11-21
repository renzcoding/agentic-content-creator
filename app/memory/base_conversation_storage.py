from abc import ABC, abstractmethod


class BaseConversationStorage(ABC):
    """Define the storage interface for conversation session data."""

    @abstractmethod
    def load(self) -> dict | list:
        """Load conversation data, including legacy list-based formats."""
        raise NotImplementedError

    @abstractmethod
    def save(self, sessions: dict[str, list[dict[str, str]]]) -> None:
        """Persist all conversation sessions to storage."""
        raise NotImplementedError
