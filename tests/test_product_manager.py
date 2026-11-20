import unittest
from unittest.mock import Mock

from app.agents.product_manager import ProductManagerAgent
from app.memory.base_memory import BaseMemory
from app.services.llm.base_provider import BaseLLMProvider


class TestProductManagerAgent(unittest.TestCase):
    """Test product manager behavior with injected dependencies."""

    def setUp(self):
        """Create mock dependencies and initialize the agent."""
        self.provider = Mock(spec=BaseLLMProvider)
        self.provider.generate.return_value = (
            "PRODUCT REQUIREMENTS\n"
            "Objective: Create a content planning dashboard\n"
            "Acceptance Criteria: Users can plan content."
        )
        self.memory = Mock(spec=BaseMemory)
        self.agent = ProductManagerAgent(
            provider=self.provider,
            memory=self.memory,
        )

    def test_generates_product_requirements(self):
        """Verify that the agent returns provider-generated requirements."""
        result = self.agent.run("Create a content planning dashboard")

        self.assertIn("PRODUCT REQUIREMENTS", result)
        self.assertIn("content planning dashboard", result)
        self.assertIn("Acceptance Criteria", result)
        self.provider.generate.assert_called_once()

    def test_rejects_empty_task(self):
        """Verify that empty tasks are rejected without calling the provider."""
        with self.assertRaises(ValueError):
            self.agent.run("   ")

        self.provider.generate.assert_not_called()

    def test_includes_remembered_context_in_prompt(self):
        """Verify that stored project context is included in the LLM prompt."""
        self.memory.retrieve.return_value = "Use React and Laravel."

        self.agent.run("Build a dashboard")

        prompt = self.provider.generate.call_args.args[0]
        self.assertIn("Previous Context: Use React and Laravel.", prompt)
        self.memory.retrieve.assert_called_once_with(
            "Product Manager:project_context"
        )

    def test_runs_without_memory_context(self):
        """Verify that missing context does not affect requirement generation."""
        self.memory.retrieve.return_value = None

        result = self.agent.run("Build a dashboard")

        prompt = self.provider.generate.call_args.args[0]
        self.assertNotIn("Previous Context:", prompt)
        self.assertIn("PRODUCT REQUIREMENTS", result)

    def test_runs_without_memory_configuration(self):
        """Verify that the agent works when memory is not configured."""
        agent = ProductManagerAgent(provider=self.provider)

        result = agent.run("Build a dashboard")

        self.assertIn("PRODUCT REQUIREMENTS", result)
        self.provider.generate.assert_called_once()


if __name__ == "__main__":
    unittest.main()
