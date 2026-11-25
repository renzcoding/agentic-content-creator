import unittest
import uuid
from unittest.mock import Mock

from app.agents.base_agent import BaseAgent
from app.memory.base_memory import BaseMemory


class ExampleAgent(BaseAgent):
    """Provide a concrete agent for testing the base interface."""

    def run(self, task: str) -> str:
        """Return the received task."""
        return task


class TestBaseAgent(unittest.TestCase):
    """Test agent identity and memory integration."""

    def setUp(self):
        """Create an agent with mocked memory storage."""
        self.memory = Mock(spec=BaseMemory)
        self.agent = ExampleAgent("Example", "Testing", self.memory)

    def test_initializes_agent_identity(self):
        self.assertEqual(self.agent.name, "Example")
        self.assertEqual(self.agent.role, "Testing")

    def test_rejects_empty_agent_name(self):
        """Verify empty agent names are rejected."""
        with self.assertRaises(ValueError):
            ExampleAgent("", "Testing")

    def test_rejects_whitespace_agent_name(self):
        """Verify whitespace-only agent names are rejected."""
        with self.assertRaises(ValueError):
            ExampleAgent("   ", "Testing")

    def test_rejects_empty_agent_role(self):
        """Verify empty agent roles are rejected."""
        with self.assertRaises(ValueError):
            ExampleAgent("Example", "")

    def test_rejects_whitespace_agent_role(self):
        """Verify whitespace-only agent roles are rejected."""
        with self.assertRaises(ValueError):
            ExampleAgent("Example", "   ")

    def test_generates_uuid_v4_when_agent_id_is_not_provided(self):
        """Verify a UUID v4 is generated automatically."""
        self.assertIsInstance(uuid.UUID(self.agent.agent_id), uuid.UUID)
        self.assertEqual(uuid.UUID(self.agent.agent_id).version, 4)

    def test_accepts_valid_uuid_v4(self):
        """Verify an existing UUID v4 is preserved."""
        expected_id = str(uuid.uuid4())
        agent = ExampleAgent("Example", "Testing", agent_id=expected_id)

        self.assertEqual(agent.agent_id, expected_id)

    def test_rejects_invalid_uuid(self):
        """Verify malformed agent identifiers are rejected."""
        with self.assertRaises(ValueError):
            ExampleAgent("Example", "Testing", agent_id="invalid-uuid")

    def test_rejects_uuid_version_other_than_four(self):
        """Verify UUID versions other than four are rejected."""
        legacy_id = str(uuid.uuid1())

        with self.assertRaises(ValueError):
            ExampleAgent("Example", "Testing", agent_id=legacy_id)

    def test_agent_id_is_read_only(self):
        """Verify the public agent identifier cannot be reassigned."""
        with self.assertRaises(AttributeError):
            self.agent.agent_id = str(uuid.uuid4())

    def test_accepts_optional_organizational_metadata(self):
        """Verify optional organizational metadata is stored."""
        agent = ExampleAgent(
            "Example",
            "Testing",
            formal_name="Example Specialist",
            division_id="engineering_technology",
            manager_agent_id=str(uuid.uuid4()),
        )

        self.assertEqual(agent.formal_name, "Example Specialist")
        self.assertEqual(agent.division_id, "engineering_technology")
        self.assertIsNotNone(agent.manager_agent_id)

    def test_defaults_optional_metadata_to_none(self):
        """Verify organizational metadata defaults to None."""
        self.assertIsNone(self.agent.formal_name)
        self.assertIsNone(self.agent.division_id)
        self.assertIsNone(self.agent.manager_agent_id)

    def test_preserves_legacy_constructor_arguments(self):
        """Verify the legacy memory argument remains compatible."""
        self.assertIs(self.agent.memory, self.memory)

    def test_rejects_incomplete_agent(self):
        with self.assertRaises(TypeError):
            BaseAgent("Example", "Testing")

    def test_remembers_information(self):
        self.agent.remember("topic", "Agentic AI")
        self.memory.save.assert_called_once_with(
            "Example:topic",
            "Agentic AI",
        )

    def test_recalls_information(self):
        self.memory.retrieve.return_value = "Agentic AI"
        result = self.agent.recall("topic")

        self.assertEqual(result, "Agentic AI")
        self.memory.retrieve.assert_called_once_with("Example:topic")

    def test_rejects_memory_without_configuration(self):
        agent = ExampleAgent("Example", "Testing")

        with self.assertRaises(RuntimeError):
            agent.remember("topic", "Agentic AI")

        with self.assertRaises(RuntimeError):
            agent.recall("topic")


if __name__ == "__main__":
    unittest.main()
