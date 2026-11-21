import json
import tempfile
import unittest
from pathlib import Path

from app.memory.conversation_memory import ConversationMemory
from app.memory.base_conversation_storage import BaseConversationStorage
from app.memory.sqlite_conversation_storage import SQLiteConversationStorage
import tempfile
from pathlib import Path


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

    def test_searches_messages_by_keyword(self):
        """Verify messages can be searched by keyword."""
        self.memory.add_message("user", "Build a React dashboard.")
        self.memory.add_message("assistant", "Use reusable React components.")
        self.memory.add_message("user", "Configure the database.")

        results = self.memory.search_messages("React")

        self.assertEqual(len(results), 2)
        self.assertIn("React", results[0]["content"])
        self.assertIn("React", results[1]["content"])

    def test_search_is_case_insensitive(self):
        """Verify keyword search ignores letter casing."""
        self.memory.add_message("user", "Build an AI assistant.")

        results = self.memory.search_messages("ai")

        self.assertEqual(len(results), 1)

    def test_searches_only_selected_session(self):
        """Verify keyword search is isolated by session."""
        self.memory.add_message("user", "Build a React app.", "session-a")
        self.memory.add_message("user", "Build a React dashboard.", "session-b")

        results = self.memory.search_messages(
            "React",
            session_id="session-a",
        )

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["content"], "Build a React app.")

    def test_limits_search_results(self):
        """Verify search limits return the newest matching messages."""
        self.memory.add_message("user", "React project one.")
        self.memory.add_message("user", "React project two.")
        self.memory.add_message("user", "React project three.")

        results = self.memory.search_messages("React", limit=2)

        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]["content"], "React project two.")
        self.assertEqual(results[1]["content"], "React project three.")

    def test_rejects_empty_search_keyword(self):
        """Verify empty search keywords are rejected."""
        with self.assertRaises(ValueError):
            self.memory.search_messages(" ")

    def test_rejects_invalid_search_limit(self):
        """Verify non-positive search limits are rejected."""
        with self.assertRaises(ValueError):
            self.memory.search_messages("React", limit=0)

    def test_rejects_empty_search_session_id(self):
        """Verify empty search session identifiers are rejected."""
        with self.assertRaises(ValueError):
            self.memory.search_messages("React", session_id=" ")

    def test_clears_conversation_history(self):
        """Verify that all conversation messages can be deleted."""
        self.memory.add_message("user", "Hello")
        self.memory.clear()

        self.assertEqual(self.memory.get_history(), [])


    def test_isolates_conversation_sessions(self):
        """Verify that different sessions have separate conversation histories."""
        self.memory.add_message("user", "Session A message", "session-a")
        self.memory.add_message("user", "Session B message", "session-b")

        history_a = self.memory.get_history(session_id="session-a")
        history_b = self.memory.get_history(session_id="session-b")

        self.assertEqual(history_a[0]["content"], "Session A message")
        self.assertEqual(history_b[0]["content"], "Session B message")

    def test_clears_only_selected_session(self):
        """Verify that clearing one session preserves other sessions."""
        self.memory.add_message("user", "Session A", "session-a")
        self.memory.add_message("user", "Session B", "session-b")

        self.memory.clear(session_id="session-a")

        self.assertEqual(self.memory.get_history(session_id="session-a"), [])
        self.assertEqual(len(self.memory.get_history(session_id="session-b")), 1)

    def test_rejects_empty_session_id(self):
        """Verify that empty session identifiers are rejected."""
        with self.assertRaises(ValueError):
            self.memory.add_message("user", "Hello", " ")

        with self.assertRaises(ValueError):
            self.memory.get_history(session_id=" ")

        with self.assertRaises(ValueError):
            self.memory.clear(session_id=" ")


    def test_migrates_legacy_list_format(self):
        """Verify that legacy messages migrate into the default session."""
        legacy_messages = [
            {"role": "user", "content": "Old question"},
            {"role": "assistant", "content": "Old answer"},
        ]
        self.memory.file_path.write_text(
            json.dumps(legacy_messages),
            encoding="utf-8",
        )

        history = self.memory.get_history()

        self.assertEqual(history, legacy_messages)

        stored_data = json.loads(
            self.memory.file_path.read_text(encoding="utf-8")
        )
        self.assertEqual(stored_data, {"default": legacy_messages})

    def test_preserves_legacy_messages_when_adding_new_message(self):
        """Verify that new messages preserve migrated legacy history."""
        legacy_messages = [
            {"role": "user", "content": "Old question"},
        ]
        self.memory.file_path.write_text(
            json.dumps(legacy_messages),
            encoding="utf-8",
        )

        self.memory.add_message("assistant", "New answer")

        history = self.memory.get_history()

        self.assertEqual(len(history), 2)
        self.assertEqual(history[0]["content"], "Old question")
        self.assertEqual(history[1]["content"], "New answer")


    def test_uses_injected_storage_backend(self):
        """Verify conversation memory uses an injected storage backend."""

        class FakeStorage(BaseConversationStorage):
            """Provide an in-memory storage implementation for testing."""

            def __init__(self):
                """Initialize empty in-memory session data."""
                self.sessions = {}

            def load(self):
                """Return stored session data."""
                return self.sessions

            def save(self, sessions):
                """Update stored session data."""
                self.sessions = sessions

        storage = FakeStorage()
        memory = ConversationMemory(storage=storage)

        memory.add_message("user", "Test injected storage.")

        self.assertEqual(
            storage.sessions["default"][0]["content"],
            "Test injected storage.",
        )
        self.assertEqual(len(memory.get_history()), 1)


    def test_integrates_with_sqlite_storage(self):
        """Verify conversation memory works with SQLite storage."""

        with tempfile.TemporaryDirectory() as temp_dir:
            database_path = Path(temp_dir) / "conversations.db"
            storage = SQLiteConversationStorage(str(database_path))
            memory = ConversationMemory(storage=storage)

            memory.add_message("user", "Hello SQLite.")
            memory.add_message("assistant", "SQLite is working.")

            history = memory.get_history()

            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["content"], "Hello SQLite.")
            self.assertEqual(history[1]["content"], "SQLite is working.")

            memory.clear()

            self.assertEqual(memory.get_history(), [])


if __name__ == "__main__":
    unittest.main()
