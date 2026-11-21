import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.memory.conversation_storage_factory import create_conversation_storage
from app.memory.conversation_memory import ConversationMemory
from app.memory.json_conversation_storage import JsonConversationStorage
from app.memory.sqlite_conversation_storage import SQLiteConversationStorage


class TestConversationStorageFactory(unittest.TestCase):
    """Test conversation storage backend creation."""

    def test_creates_json_storage(self):
        """Verify that JSON configuration creates JSON storage."""
        with patch("app.memory.conversation_storage_factory.settings") as settings:
            settings.CONVERSATION_STORAGE_BACKEND = "json"
            settings.CONVERSATION_JSON_PATH = "outputs/test.json"

            storage = create_conversation_storage()

            self.assertIsInstance(storage, JsonConversationStorage)

    def test_creates_sqlite_storage(self):
        """Verify that SQLite configuration creates SQLite storage."""
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = str(Path(temp_dir) / "test.db")

            with patch("app.memory.conversation_storage_factory.settings") as settings:
                settings.CONVERSATION_STORAGE_BACKEND = "sqlite"
                settings.CONVERSATION_SQLITE_PATH = database_path

                storage = create_conversation_storage()

                self.assertIsInstance(storage, SQLiteConversationStorage)

    def test_rejects_unsupported_backend(self):
        """Verify that unsupported storage backends raise an error."""
        with patch("app.memory.conversation_storage_factory.settings") as settings:
            settings.CONVERSATION_STORAGE_BACKEND = "unsupported"

            with self.assertRaises(ValueError):
                create_conversation_storage()


    def test_conversation_memory_preserves_custom_json_path(self):
        """Verify legacy file_path configuration remains supported."""
        with tempfile.TemporaryDirectory() as temp_dir:
            custom_path = str(Path(temp_dir) / "custom.json")

            with patch("app.memory.conversation_storage_factory.settings") as settings:
                settings.CONVERSATION_STORAGE_BACKEND = "json"
                settings.CONVERSATION_JSON_PATH = "outputs/default.json"

                memory = ConversationMemory(file_path=custom_path)

                self.assertEqual(memory.file_path, Path(custom_path))


    def test_conversation_memory_uses_configured_json_path(self):
        """Verify application settings determine the default JSON path."""
        with tempfile.TemporaryDirectory() as temp_dir:
            configured_path = str(Path(temp_dir) / "configured.json")

            with patch("app.memory.conversation_storage_factory.settings") as settings:
                settings.CONVERSATION_STORAGE_BACKEND = "json"
                settings.CONVERSATION_JSON_PATH = configured_path

                memory = ConversationMemory()

                self.assertEqual(memory.file_path, Path(configured_path))


    def test_conversation_memory_uses_configured_sqlite_backend(self):
        """Verify application settings select SQLite for conversation memory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = str(Path(temp_dir) / "configured.db")

            with patch("app.memory.conversation_storage_factory.settings") as settings:
                settings.CONVERSATION_STORAGE_BACKEND = "sqlite"
                settings.CONVERSATION_SQLITE_PATH = database_path

                memory = ConversationMemory()

                self.assertIsInstance(memory.storage, SQLiteConversationStorage)
                self.assertEqual(memory.storage.database_path, Path(database_path))


if __name__ == "__main__":
    unittest.main()
