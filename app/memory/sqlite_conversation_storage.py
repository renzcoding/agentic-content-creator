import sqlite3
from contextlib import closing
from pathlib import Path

from app.memory.base_conversation_storage import BaseConversationStorage
from app.memory.conversation_data_validator import ConversationDataValidator


class SQLiteConversationStorage(BaseConversationStorage):
    """Persist conversation sessions in a SQLite database."""

    def __init__(
        self,
        database_path: str = "outputs/conversations.db",
    ) -> None:
        """Initialize the database and create the messages table."""
        self.database_path = Path(database_path)
        self.database_path.parent.mkdir(parents=True, exist_ok=True)

        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT NOT NULL,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL
                )
                """
            )

    def load(self) -> dict | list:
        """Load all conversation messages grouped by session."""
        sessions = {}

        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            rows = connection.execute(
                """
                SELECT session_id, role, content
                FROM conversation_messages
                ORDER BY id ASC
                """
            ).fetchall()

        for session_id, role, content in rows:
            sessions.setdefault(session_id, []).append({
                "role": role,
                "content": content,
            })

        ConversationDataValidator.validate(sessions)
        return sessions

    def save(self, sessions: dict[str, list[dict[str, str]]]) -> None:
        """Validate and replace stored conversation session data."""
        ConversationDataValidator.validate(sessions)
        with closing(sqlite3.connect(self.database_path)) as connection, connection:
            connection.execute("DELETE FROM conversation_messages")

            connection.executemany(
                """
                INSERT INTO conversation_messages (session_id, role, content)
                VALUES (?, ?, ?)
                """,
                [
                    (session_id, message["role"], message["content"])
                    for session_id, messages in sessions.items()
                    for message in messages
                ],
            )
