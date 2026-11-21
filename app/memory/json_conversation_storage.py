import json
from pathlib import Path

from app.memory.base_conversation_storage import BaseConversationStorage


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
            return json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

    def save(self, sessions: dict[str, list[dict[str, str]]]) -> None:
        """Write conversation sessions to the JSON file."""
        self.file_path.write_text(
            json.dumps(sessions, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )
