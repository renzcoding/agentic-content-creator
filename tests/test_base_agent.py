import unittest

from app.agents.base_agent import BaseAgent


class TestBaseAgent(unittest.TestCase):
    """Test the base agent interface and required implementation."""

    def test_initializes_agent_identity(self):
        """Verify that agent name and role are stored."""
        class ExampleAgent(BaseAgent):
            def run(self, task: str) -> str:
                return task

        agent = ExampleAgent("Example", "Testing")

        self.assertEqual(agent.name, "Example")
        self.assertEqual(agent.role, "Testing")

    def test_rejects_incomplete_agent(self):
        """Verify that subclasses must implement run."""
        with self.assertRaises(TypeError):
            BaseAgent("Example", "Testing")


if __name__ == "__main__":
    unittest.main()
