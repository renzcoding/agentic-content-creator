import unittest

from app.agents.product_manager import ProductManagerAgent


class TestProductManagerAgent(unittest.TestCase):
    """Test product manager behavior."""

    def setUp(self):
        """Create a product manager for each test."""
        self.agent = ProductManagerAgent()

    def test_returns_product_requirements(self):
        """Verify that a task produces a requirements brief."""
        result = self.agent.run("Create a content planning dashboard")

        self.assertIn("PRODUCT REQUIREMENTS", result)
        self.assertIn("content planning dashboard", result)
        self.assertIn("acceptance criteria", result)

    def test_rejects_empty_task(self):
        """Verify that empty tasks are rejected."""
        with self.assertRaises(ValueError):
            self.agent.run("   ")


if __name__ == "__main__":
    unittest.main()
