
import unittest
from unittest.mock import Mock
from app.agents.product_manager import ProductManagerAgent
from app.agents.base_agent import BaseAgent
from app.agents.orchestrator import AgentOrchestrator


class StubAgent(BaseAgent):
    """Provide a lightweight agent for orchestrator testing."""

    def run(self, task: str) -> str:
        """Return a predictable response for the supplied task."""
        return f"Processed: {task}"


class TestAgentOrchestrator(unittest.TestCase):
    """Test agent registration and task execution."""

    def setUp(self):
        """Create a fresh orchestrator and test agent."""
        self.orchestrator = AgentOrchestrator()
        self.agent = StubAgent("Test Agent", "Testing")

    def test_registers_agent(self):
        """Verify that an agent can be registered."""
        self.orchestrator.register_agent(self.agent)

        self.assertIn("test agent", self.orchestrator.agents)

    def test_rejects_duplicate_agent(self):
        """Verify that duplicate agent names are rejected."""
        self.orchestrator.register_agent(self.agent)

        with self.assertRaises(ValueError):
            self.orchestrator.register_agent(self.agent)

    def test_rejects_empty_agent_name(self):
        """Verify that agents with empty names cannot be registered."""
        agent = StubAgent(" ", "Testing")

        with self.assertRaises(ValueError):
            self.orchestrator.register_agent(agent)

    def test_executes_registered_agent(self):
        """Verify that tasks are delegated to the correct agent."""
        self.orchestrator.register_agent(self.agent)

        result = self.orchestrator.execute("TEST AGENT", "Create a plan")

        self.assertEqual(result, "Processed: Create a plan")

    def test_rejects_unregistered_agent(self):
        """Verify that unknown agents cannot execute tasks."""
        with self.assertRaises(ValueError):
            self.orchestrator.execute("Unknown Agent", "Create a plan")

    def test_executes_product_manager_agent(self):
        """Verify that the orchestrator executes a real agent with a mocked provider."""

        # Create a mock provider to avoid calling the Ollama API.
        mock_provider = Mock()
        mock_provider.generate.return_value = "Product requirements generated."

        # Initialize and register the product manager agent.
        product_manager = ProductManagerAgent(provider=mock_provider)
        self.orchestrator.register_agent(product_manager)

        # Execute a task through the orchestrator.
        result = self.orchestrator.execute(
            "Product Manager",
            "Build an AI content creator",
        )

        self.assertEqual(result, "Product requirements generated.")
        mock_provider.generate.assert_called_once()



    def test_lists_registered_agents(self):
        """Verify that registered agent names and roles are returned."""

        # Register the test agent before requesting the agent list.
        self.orchestrator.register_agent(self.agent)

        result = self.orchestrator.list_agents()

        self.assertEqual(
            result,
            [
                {
                    "name": "Test Agent",
                    "role": "Testing",
                }
            ],
        )

    def test_returns_empty_list_when_no_agents_registered(self):
        """Verify that an empty registry returns an empty list."""
        self.assertEqual(self.orchestrator.list_agents(), [])



if __name__ == "__main__":
    unittest.main()
