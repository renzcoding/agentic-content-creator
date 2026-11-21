import json
import tempfile
import unittest
from pathlib import Path

from app.memory.json_conversation_storage import JsonConversationStorage


class TestJsonConversationStorage(unittest.TestCase):
    """Test JSON-based conversation storage."""

    def setUp(self):
        """Create an isolated temporary storage directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "conversations.json"
        self.storage = JsonConversationStorage(str(self.file_path))

    def tearDown(self):
        """Remove temporary test files."""
        self.temp_dir.cleanup()

    def test_returns_empty_dictionary_when_file_is_missing(self):
        """Verify missing storage files return an empty dictionary."""
        self.assertEqual(self.storage.load(), {})

    def test_saves_and_loads_sessions(self):
        """Verify conversation sessions persist correctly."""
        sessions = {
            "default": [
                {"role": "user", "content": "Hello"}
            ]
        }

        self.storage.save(sessions)

        self.assertEqual(self.storage.load(), sessions)

    def test_loads_legacy_list_format(self):
        """Verify legacy list data can be loaded before migration."""
        legacy_data = [
            {"role": "user", "content": "Old message"}
        ]
        self.file_path.write_text(
            json.dumps(legacy_data),
            encoding="utf-8",
        )

        self.assertEqual(self.storage.load(), legacy_data)

    def test_returns_empty_dictionary_for_invalid_json(self):
        """Verify invalid JSON does not crash storage loading."""
        self.file_path.write_text("{invalid", encoding="utf-8")

        self.assertEqual(self.storage.load(), {})


if __name__ == "__main__":
    unittest.main()
