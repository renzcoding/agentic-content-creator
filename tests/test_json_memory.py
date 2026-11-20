import json
import tempfile
import unittest
from pathlib import Path

from app.memory.json_memory import JsonMemory


class TestJsonMemory(unittest.TestCase):
    """Test local JSON memory storage."""

    def setUp(self) -> None:
        """Create an isolated temporary storage directory."""
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = Path(self.temp_dir.name) / "memory.json"
        self.memory = JsonMemory(str(self.file_path))

    def tearDown(self) -> None:
        """Remove temporary test files."""
        self.temp_dir.cleanup()

    def test_saves_and_retrieves_memory(self):
        self.memory.save("topic", "AI Agents")
        self.assertEqual(self.memory.retrieve("topic"), "AI Agents")

    def test_updates_existing_memory(self):
        self.memory.save("topic", "AI")
        self.memory.save("topic", "Agentic AI")
        self.assertEqual(self.memory.retrieve("topic"), "Agentic AI")

    def test_returns_none_for_missing_memory(self):
        self.assertIsNone(self.memory.retrieve("missing"))

    def test_rejects_empty_key(self):
        with self.assertRaises(ValueError):
            self.memory.save(" ", "value")

    def test_rejects_empty_value(self):
        with self.assertRaises(ValueError):
            self.memory.save("key", " ")

    def test_clears_all_memories(self):
        self.memory.save("topic", "AI")
        self.memory.clear()
        self.assertIsNone(self.memory.retrieve("topic"))

    def test_persists_memory_across_instances(self):
        self.memory.save("topic", "Agentic AI")
        new_memory = JsonMemory(str(self.file_path))
        self.assertEqual(new_memory.retrieve("topic"), "Agentic AI")


if __name__ == "__main__":
    unittest.main()
