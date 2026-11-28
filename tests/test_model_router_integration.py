import unittest
from unittest.mock import Mock

from app.agents.product_manager import ProductManagerAgent
from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.model_configuration import ModelConfiguration
from app.services.llm.model_health_checker import ModelHealthChecker
from app.services.llm.model_registry import ModelRegistry
from app.services.llm.model_router import ModelRouter
from app.services.llm.model_selection_policy import ModelSelectionPolicy
from app.services.llm.model_usage_tracker import ModelUsageTracker


class FakeProvider(BaseLLMProvider):
    """Provide deterministic responses for integration tests."""

    def __init__(self, response: str) -> None:
        """Initialize the provider with a fixed response."""
        self.response = response
        self.received_prompts = []

    def generate(self, prompt: str) -> str:
        """Record the prompt and return the configured response."""
        self.received_prompts.append(prompt)
        return self.response


class TestProductManagerModelRouterIntegration(unittest.TestCase):
    """Verify ProductManagerAgent can use ModelRouter as its provider."""

    def test_product_manager_generates_through_model_router(self):
        """Verify prompt delegation, response delivery, and usage tracking."""
        expected_response = (
            "PRODUCT REQUIREMENTS\n"
            "Objective: Build a content planning dashboard.\n"
            "Scope: Create and manage content plans.\n"
            "User Needs: Organize content production.\n"
            "Acceptance Criteria: Users can save content plans."
        )

        registry = ModelRegistry()
        configuration = ModelConfiguration(
            model_id="local-qwen",
            provider_id="ollama",
            model_name="qwen2.5:0.5b",
            is_local=True,
            capabilities=("text-generation",),
            input_cost_per_1k_tokens=1.0,
            output_cost_per_1k_tokens=1.0,
        )
        registry.register(configuration)

        fake_provider = FakeProvider(expected_response)
        usage_tracker = ModelUsageTracker()
        health_checker = ModelHealthChecker(
            Mock(return_value=True)
        )

        router = ModelRouter(
            registry=registry,
            selection_policy=ModelSelectionPolicy(registry),
            health_checker=health_checker,
            usage_tracker=usage_tracker,
            providers={"ollama": fake_provider},
        )

        agent = ProductManagerAgent(provider=router)

        result = agent.run("Create a content planning dashboard")

        self.assertEqual(result, expected_response)
        self.assertEqual(len(fake_provider.received_prompts), 1)
        self.assertIn(
            "Create a content planning dashboard",
            fake_provider.received_prompts[0],
        )
        self.assertEqual(
            router.last_selected_model_id,
            "local-qwen",
        )

        usage = usage_tracker.get_usage("local-qwen")
        self.assertEqual(usage["request_count"], 1)
        self.assertGreater(usage["input_tokens"], 0)
        self.assertGreater(usage["output_tokens"], 0)


if __name__ == "__main__":
    unittest.main()
