import json
from pathlib import Path

from app.memory.base_memory import BaseMemory


class JsonMemory(BaseMemory):
    """Store agent memories in a local JSON file."""

    def __init__(self, file_path: str = "outputs/memory.json") -> None:
        """Initialize memory storage and create its parent directory."""
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)

    def _load(self) -> dict[str, str]:
        """Load stored memories or return an empty dictionary."""
        if not self.file_path.exists():
            return {}

        try:
            data = json.loads(self.file_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            return {}

        return data if isinstance(data, dict) else {}

    def save(self, key: str, value: str) -> None:
        """Save or update a memory entry."""
        if not key.strip():
            raise ValueError("Memory key must not be empty.")

        if not value.strip():
            raise ValueError("Memory value must not be empty.")

        memories = self._load()
        memories[key.strip()] = value.strip()

        self.file_path.write_text(
            json.dumps(memories, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def retrieve(self, key: str) -> str | None:
        """Retrieve a memory entry by its key."""
        return self._load().get(key.strip())

    def clear(self) -> None:
        """Delete all stored memory entries."""
        self.file_path.write_text("{}", encoding="utf-8")
