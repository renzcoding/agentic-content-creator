import unittest
from unittest.mock import Mock

from app.agents.product_manager import ProductManagerAgent
from app.services.llm.base_provider import BaseLLMProvider


class TestProductManagerAgent(unittest.TestCase):
    """Test product manager behavior with an injected LLM provider."""

    def setUp(self):
        """Create a mock provider and inject it into the agent."""
        self.provider = Mock(spec=BaseLLMProvider)
        self.provider.generate.return_value = (
            "PRODUCT REQUIREMENTS\n"
            "Objective: Create a content planning dashboard\n"
            "Acceptance Criteria: Users can plan content."
        )
        self.agent = ProductManagerAgent(provider=self.provider)

    def test_generates_product_requirements(self):
        """Verify that the agent returns the provider-generated requirements."""
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


if __name__ == "__main__":
    unittest.main()
