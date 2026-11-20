import unittest
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
