import json
from pathlib import Path


class ConversationMemory:
    """Persist conversation messages in a local JSON file."""

    def __init__(self, file_path: str = "outputs/conversations.json") -> None:
        """Initialize conversation storage."""
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> list[dict[str, str]]:
        """Load conversation messages or return an empty list."""
        if not self.file_path.exists():
            return []

        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return []

        return data if isinstance(data, list) else []

    def add_message(self, role: str, content: str) -> None:
        """Append a validated message to conversation history."""
        if not role.strip():
            raise ValueError("Message role must not be empty.")

        if not content.strip():
            raise ValueError("Message content must not be empty.")

        messages = self._load()
        messages.append({
            "role": role.strip(),
            "content": content.strip(),
        })

        self.file_path.write_text(
            json.dumps(messages, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def get_history(self, limit: int | None = None) -> list[dict[str, str]]:
        """Return conversation history, optionally limited to recent messages."""
        messages = self._load()

        if limit is not None:
            if limit < 1:
                raise ValueError("History limit must be greater than zero.")
            return messages[-limit:]

        return messages

    def clear(self) -> None:
        """Remove all conversation messages."""
        self.file_path.write_text("[]", encoding="utf-8")
