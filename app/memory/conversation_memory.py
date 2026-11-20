import json
from pathlib import Path


class ConversationMemory:
    """Persist conversation messages separately for each session."""

    def __init__(self, file_path: str = "outputs/conversations.json") -> None:
        """Initialize session-based conversation storage."""
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, list[dict[str, str]]]:
        """Load sessions and migrate legacy conversation data when needed."""
        if not self.file_path.exists():
            return {}

        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

        # Migrate legacy list-based history into the default session.
        if isinstance(data, list):
            sessions = {"default": data}

            self.file_path.write_text(
                json.dumps(sessions, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
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

        self.file_path.write_text(
            json.dumps(sessions, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

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

    def clear(self, session_id: str = "default") -> None:
        """Remove conversation history from the selected session."""
        if not session_id.strip():
            raise ValueError("Session ID must not be empty.")

        sessions = self._load()
        sessions.pop(session_id.strip(), None)

        self.file_path.write_text(
            json.dumps(sessions, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
