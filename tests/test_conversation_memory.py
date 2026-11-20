import tempfile
import unittest
from pathlib import Path

from app.memory.conversation_memory import ConversationMemory


class TestConversationMemory(unittest.TestCase):
    """Test persistent conversation history storage."""

    def setUp(self):
        """Create temporary conversation storage."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "conversations.json"
        self.memory = ConversationMemory(str(self.file_path))

    def tearDown(self):
        """Remove temporary test storage."""
        self.temp_dir.cleanup()

    def test_adds_and_retrieves_messages(self):
        """Verify that conversation messages are stored and retrieved."""
        self.memory.add_message("user", "Build a dashboard.")
        self.memory.add_message("assistant", "Let's define the requirements.")

        history = self.memory.get_history()

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["role"], "user")
        self.assertEqual(history[1]["role"], "assistant")

    def test_persists_history_across_instances(self):
        """Verify that history survives new memory instances."""
        self.memory.add_message("user", "Remember this conversation.")

        new_memory = ConversationMemory(str(self.file_path))

        self.assertEqual(len(new_memory.get_history()), 1)

    def test_returns_only_recent_messages(self):
        """Verify that history limits return the newest messages."""
        self.memory.add_message("user", "First")
        self.memory.add_message("assistant", "Second")
        self.memory.add_message("user", "Third")

        history = self.memory.get_history(limit=2)

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "Second")
        self.assertEqual(history[1]["content"], "Third")

    def test_rejects_empty_role(self):
        """Verify that empty message roles are rejected."""
        with self.assertRaises(ValueError):
            self.memory.add_message(" ", "Hello")

    def test_rejects_empty_content(self):
        """Verify that empty message content is rejected."""
        with self.assertRaises(ValueError):
            self.memory.add_message("user", " ")

    def test_rejects_invalid_history_limit(self):
        """Verify that non-positive history limits are rejected."""
        with self.assertRaises(ValueError):
            self.memory.get_history(limit=0)

    def test_clears_conversation_history(self):
        """Verify that all conversation messages can be deleted."""
        self.memory.add_message("user", "Hello")
        self.memory.clear()

        self.assertEqual(self.memory.get_history(), [])


if __name__ == "__main__":
    unittest.main()
