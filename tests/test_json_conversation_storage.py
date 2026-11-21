import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

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

    def test_preserves_existing_data_when_temporary_write_fails(self):
        """Verify failed temporary writes do not corrupt existing data."""
        original_data = {"default": [{"role": "user", "content": "Original"}]}
        self.storage.save(original_data)

        with patch.object(Path, "write_text", side_effect=OSError("Write failed")):
            with self.assertRaises(OSError):
                self.storage.save({"default": [{"role": "user", "content": "New"}]})

        self.assertEqual(self.storage.load(), original_data)

        temporary_path = self.file_path.with_suffix(".json.tmp")
        self.assertFalse(temporary_path.exists())

    def test_replaces_existing_data_after_successful_save(self):
        """Verify successful atomic writes replace existing conversation data."""
        original_data = {"default": [{"role": "user", "content": "Original"}]}
        updated_data = {"default": [{"role": "user", "content": "Updated"}]}

        self.storage.save(original_data)
        self.storage.save(updated_data)

        self.assertEqual(self.storage.load(), updated_data)


    def test_rejects_invalid_conversation_data(self):
        """Verify invalid conversation data is rejected before persistence."""
        invalid_sessions = {
            "default": [
                {"role": "user", "content": None},
            ]
        }

        with self.assertRaises(ValueError):
            self.storage.save(invalid_sessions)

        self.assertEqual(self.storage.load(), {})


if __name__ == "__main__":
    unittest.main()
