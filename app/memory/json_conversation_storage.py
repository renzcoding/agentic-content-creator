import json
from pathlib import Path

from app.memory.base_conversation_storage import BaseConversationStorage
from app.memory.conversation_data_validator import ConversationDataValidator


class JsonConversationStorage(BaseConversationStorage):
    """Persist conversation session data in a JSON file."""

    def __init__(self, file_path: str = "outputs/conversations.json") -> None:
        """Initialize the JSON storage file and its parent directory."""
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def load(self) -> dict | list:
        """Load conversation data, returning an empty dictionary when unavailable."""
        if not self.file_path.exists():
            return {}

        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
            if isinstance(data, dict):
                ConversationDataValidator.validate(data)
            elif isinstance(data, list):
                ConversationDataValidator.validate({"default": data})
            else:
                raise ValueError("Unsupported conversation data format.")
            return data
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self, sessions: dict[str, list[dict[str, str]]]) -> None:
        """Validate and atomically persist conversation session data."""
        ConversationDataValidator.validate(sessions)
        temporary_path = self.file_path.with_suffix(
            f"{self.file_path.suffix}.tmp"
        )

        try:
            temporary_path.write_text(
                json.dumps(sessions, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )
            temporary_path.replace(self.file_path)
        finally:
            # Remove leftover temporary files after failed writes.
            if temporary_path.exists():
                temporary_path.unlink()
