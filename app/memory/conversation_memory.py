import re
from pathlib import Path

from app.memory.base_conversation_storage import BaseConversationStorage
from app.memory.conversation_data_validator import ConversationDataValidator
from app.memory.conversation_storage_factory import create_conversation_storage
from config import settings


class ConversationMemory:
    """Manage conversation history independently from storage implementation."""

    def __init__(
        self,
        file_path: str | None = None,
        storage: BaseConversationStorage | None = None,
    ) -> None:
        """Initialize conversation memory with an injectable storage backend."""

        # Validate the optional storage path before creating a backend.
        if file_path is not None:
            if not isinstance(file_path, str):
                raise TypeError("File path must be a string or None.")

            if not file_path.strip():
                raise ValueError("File path must not be empty.")

        # Validate injected storage against the shared storage contract.
        if storage is not None and not isinstance(storage, BaseConversationStorage):
            raise TypeError("Storage must implement BaseConversationStorage.")

        self.storage = (
            storage
            if storage is not None
            else create_conversation_storage(file_path)
        )
        self.file_path = getattr(
            self.storage,
            "file_path",
            Path(file_path or settings.CONVERSATION_JSON_PATH),
        )

    @staticmethod
    def _validate_non_empty_string(value: str, field_name: str) -> str:
        """Validate a required string and return its normalized value."""
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        if not value.strip():
            raise ValueError(f"{field_name} must not be empty.")

        return value.strip()

    @staticmethod
    def _validate_limit(limit: int | None, field_name: str) -> None:
        """Ensure an optional result limit is a positive integer."""
        if limit is None:
            return

        if not isinstance(limit, int) or isinstance(limit, bool):
            raise TypeError(f"{field_name} must be an integer or None.")

        if limit < 1:
            raise ValueError(f"{field_name} must be greater than zero.")


    def _load(self) -> dict[str, list[dict[str, str]]]:
        """Load and validate sessions while migrating legacy conversation data."""
        data = self.storage.load()

        # Migrate legacy list-based history into the default session.
        if isinstance(data, list):
            sessions = {"default": data}
            ConversationDataValidator.validate(sessions)
            self.storage.save(sessions)
            return sessions

        if not isinstance(data, dict):
            raise ValueError(
                "Conversation storage must return a dictionary or legacy list."
            )

        # Validate data returned by every storage implementation.
        ConversationDataValidator.validate(data)

        return data

    def add_message(
        self,
        role: str,
        content: str,
        session_id: str = "default",
    ) -> None:
        """Append a validated message to the selected session."""
        role = self._validate_non_empty_string(role, "Message role")
        content = self._validate_non_empty_string(content, "Message content")
        session_id = self._validate_non_empty_string(session_id, "Session ID")

        sessions = self._load()
        messages = sessions.setdefault(session_id.strip(), [])

        messages.append({
            "role": role.strip(),
            "content": content.strip(),
        })

        self.storage.save(sessions)

    def get_history(
        self,
        limit: int | None = None,
        session_id: str = "default",
    ) -> list[dict[str, str]]:
        """Retrieve conversation history from the selected session."""
        session_id = self._validate_non_empty_string(session_id, "Session ID")
        self._validate_limit(limit, "History limit")

        messages = self._load().get(session_id.strip(), [])

        return messages[-limit:] if limit is not None else messages

    def search_messages(
        self,
        keyword: str | list[str],
        session_id: str = "default",
        limit: int | None = None,
    ) -> list[dict[str, str]]:
        """Search and rank conversation messages by keyword relevance."""
        session_id = self._validate_non_empty_string(session_id, "Session ID")
        self._validate_limit(limit, "Search limit")

        # Ensure search keywords use the supported input structure.
        if isinstance(keyword, str):
            keywords = [keyword]
        elif isinstance(keyword, list):
            keywords = keyword
        else:
            raise TypeError("Search keyword must be a string or list of strings.")

        # Validate every keyword before performing the search.
        normalized_keywords = {
            self._validate_non_empty_string(item, "Search keyword").casefold()
            for item in keywords
        }

        if not normalized_keywords:
            raise ValueError("Search keyword must not be empty.")

        # Calculate how many unique keywords match each message.
        messages = self._load().get(session_id.strip(), [])
        ranked_messages = []

        for index, message in enumerate(messages):
            content = message["content"].casefold()
            score = sum(
                1
                for item in normalized_keywords
                if re.search(
                    rf"\b{re.escape(item)}\b",
                    content,
                )
            )

            if score > 0:
                ranked_messages.append((score, index, message))

        # Rank higher scores first and preserve order for equal scores.
        ranked_messages.sort(
            key=lambda item: (-item[0], item[1])
        )

        results = [
            message
            for _, _, message in ranked_messages
        ]

        return results[:limit] if limit is not None else results

    def clear(self, session_id: str = "default") -> None:
        """Remove conversation history from the selected session."""
        session_id = self._validate_non_empty_string(session_id, "Session ID")

        sessions = self._load()
        sessions.pop(session_id.strip(), None)

        self.storage.save(sessions)
