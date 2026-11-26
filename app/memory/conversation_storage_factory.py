from app.memory.base_conversation_storage import BaseConversationStorage
from app.memory.json_conversation_storage import JsonConversationStorage
from app.memory.sqlite_conversation_storage import SQLiteConversationStorage
from config import settings


def create_conversation_storage(
    file_path: str | None = None,
) -> BaseConversationStorage:
    """Create a conversation storage backend from application settings."""
    backend = settings.CONVERSATION_STORAGE_BACKEND.lower()

    if backend == "json":
        return JsonConversationStorage(
            file_path or settings.CONVERSATION_JSON_PATH
        )

    if backend == "sqlite":
        return SQLiteConversationStorage(
            file_path or settings.CONVERSATION_SQLITE_PATH
        )

    raise ValueError(f"Unsupported conversation storage backend: {backend}")
