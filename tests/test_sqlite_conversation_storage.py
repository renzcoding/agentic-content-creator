import tempfile
import unittest
from pathlib import Path

from app.memory.sqlite_conversation_storage import SQLiteConversationStorage


class TestSQLiteConversationStorage(unittest.TestCase):
    """Test SQLite-based conversation storage."""

    def setUp(self):
        """Create an isolated temporary database for each test."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.database_path = Path(self.temp_dir.name) / "conversations.db"
        self.storage = SQLiteConversationStorage(str(self.database_path))

    def tearDown(self):
        """Remove temporary database files after each test."""
        self.temp_dir.cleanup()

    def test_returns_empty_dictionary_when_database_is_empty(self):
        """Verify that an empty database returns no sessions."""
        self.assertEqual(self.storage.load(), {})

    def test_saves_and_loads_multiple_sessions(self):
        """Verify that messages persist independently across sessions."""
        sessions = {
            "session_a": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
            ],
            "session_b": [
                {"role": "user", "content": "Another session"},
            ],
        }

        self.storage.save(sessions)

        self.assertEqual(self.storage.load(), sessions)

    def test_preserves_message_order(self):
        """Verify that messages retain their original insertion order."""
        sessions = {
            "default": [
                {"role": "user", "content": "First"},
                {"role": "assistant", "content": "Second"},
                {"role": "user", "content": "Third"},
            ]
        }

        self.storage.save(sessions)

        self.assertEqual(self.storage.load(), sessions)

    def test_replaces_existing_data(self):
        """Verify that saving new data replaces previous conversations."""
        self.storage.save({
            "old_session": [
                {"role": "user", "content": "Old message"},
            ]
        })

        new_sessions = {
            "new_session": [
                {"role": "user", "content": "New message"},
            ]
        }

        self.storage.save(new_sessions)

        self.assertEqual(self.storage.load(), new_sessions)


if __name__ == "__main__":
    unittest.main()
