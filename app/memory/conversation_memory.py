import re
from pathlib import Path

from app.memory.base_conversation_storage import BaseConversationStorage
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

    def _load(self) -> dict[str, list[dict[str, str]]]:
        """Load sessions and migrate legacy conversation data when needed."""
        data = self.storage.load()

        # Migrate legacy list-based history into the default session.
        if isinstance(data, list):
            sessions = {"default": data}
            self.storage.save(sessions)
            return sessions

        return data if isinstance(data, dict) else {}

    def add_message(
        self,
        role: str,
        content: str,
        session_id: str = "default",
    ) -> None:
        """Append a validated message to the selected session."""
        if not role.strip():
            raise ValueError("Message role must not be empty.")

        if not content.strip():
            raise ValueError("Message content must not be empty.")

        if not session_id.strip():
            raise ValueError("Session ID must not be empty.")

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
        if not session_id.strip():
            raise ValueError("Session ID must not be empty.")

        if limit is not None and limit < 1:
            raise ValueError("History limit must be greater than zero.")

        messages = self._load().get(session_id.strip(), [])

        return messages[-limit:] if limit is not None else messages

    def search_messages(
        self,
        keyword: str | list[str],
        session_id: str = "default",
        limit: int | None = None,
    ) -> list[dict[str, str]]:
        """Search and rank conversation messages by keyword relevance."""
        if not session_id.strip():
            raise ValueError("Session ID must not be empty.")

        if limit is not None and limit < 1:
            raise ValueError("Search limit must be greater than zero.")

        # Normalize one or multiple search keywords.
        keywords = (
            [keyword]
            if isinstance(keyword, str)
            else keyword
        )

        normalized_keywords = {
            item.strip().casefold()
            for item in keywords
            if isinstance(item, str) and item.strip()
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
        if not session_id.strip():
            raise ValueError("Session ID must not be empty.")

        sessions = self._load()
        sessions.pop(session_id.strip(), None)

        self.storage.save(sessions)
