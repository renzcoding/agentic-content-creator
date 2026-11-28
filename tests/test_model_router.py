import unittest
from unittest.mock import Mock

from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.model_configuration import ModelConfiguration
from app.services.llm.model_budget_manager import (
    BudgetExceededError,
    ModelBudgetManager,
)
from app.services.llm.model_health_checker import ModelHealthChecker
from app.services.llm.model_registry import ModelRegistry
from app.services.llm.model_router import ModelRouter
from app.services.llm.model_selection_policy import ModelSelectionPolicy
from app.services.llm.model_usage_tracker import ModelUsageTracker


class FakeProvider(BaseLLMProvider):
    """Provide deterministic text generation for router tests."""

    def __init__(self, response="Generated response"):
        """Initialize the fake provider with a configured response."""
        self.response = response
        self.received_prompts = []

    def generate(self, prompt: str) -> str:
        """Record the prompt and return the configured response."""
        self.received_prompts.append(prompt)
        return self.response


class TestModelRouter(unittest.TestCase):
    """Test model routing, provider delegation, and usage tracking."""

    def setUp(self):
        """Initialize reusable routing dependencies."""
        self.registry = ModelRegistry()
        self.local_model = ModelConfiguration(
            model_id="local-qwen",
            provider_id="ollama",
            model_name="qwen2.5:0.5b",
            is_local=True,
            capabilities=("text-generation",),
            input_cost_per_1k_tokens=1.0,
            output_cost_per_1k_tokens=1.0,
        )
        self.registry.register(self.local_model)

        self.provider = FakeProvider()
        self.health_check = Mock(return_value=True)
        self.health_checker = ModelHealthChecker(self.health_check)
        self.selection_policy = ModelSelectionPolicy(self.registry)
        self.usage_tracker = ModelUsageTracker()

        self.router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={"ollama": self.provider},
        )

    def test_implements_base_provider_contract(self):
        """Ensure the router implements the existing provider contract."""
        self.assertIsInstance(self.router, BaseLLMProvider)

    def test_generates_response_using_local_provider(self):
        """Verify successful generation through the selected provider."""
        response = self.router.generate("Create a project plan")

        self.assertEqual(response, "Generated response")
        self.assertEqual(
            self.provider.received_prompts,
            ["Create a project plan"],
        )
        self.assertEqual(
            self.router.last_selected_model_id,
            "local-qwen",
        )

    def test_clears_last_selected_model_after_failed_generation(self):
        """Ensure failed requests do not retain stale selection metadata."""
        self.router.generate("First successful request")
        self.assertEqual(
            self.router.last_selected_model_id,
            "local-qwen",
        )

        self.health_check.return_value = False

        with self.assertRaisesRegex(RuntimeError, "unhealthy"):
            self.router.generate("Second failed request")

        self.assertIsNone(self.router.last_selected_model_id)

    def test_records_usage_after_successful_generation(self):
        """Verify estimated token usage is recorded after generation."""
        self.router.generate("Create a project plan")

        usage = self.usage_tracker.get_usage("local-qwen")

        self.assertEqual(usage["request_count"], 1)
        self.assertGreater(usage["input_tokens"], 0)
        self.assertGreater(usage["output_tokens"], 0)

    def test_does_not_record_usage_when_generation_fails(self):
        """Ensure failed generation does not create usage records."""
        self.provider.response = ""

        with self.assertRaises(RuntimeError):
            self.router.generate("Create a project plan")

        usage = self.usage_tracker.get_usage("local-qwen")

        self.assertEqual(usage["request_count"], 0)

    def test_rejects_unhealthy_model(self):
        """Ensure unhealthy models are rejected before generation."""
        self.health_check.return_value = False

        with self.assertRaisesRegex(RuntimeError, "unhealthy"):
            self.router.generate("Create a project plan")

        self.assertEqual(self.provider.received_prompts, [])

    def test_rejects_unregistered_provider(self):
        """Ensure routing fails when no provider adapter is registered."""
        provider_model = ModelConfiguration(
            model_id="missing-provider-model",
            provider_id="missing",
            model_name="missing-model",
            is_local=True,
        )
        self.registry.register(provider_model)

        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={"ollama": self.provider},
            preferred_model_id="missing-provider-model",
        )

        with self.assertRaisesRegex(RuntimeError, "No provider registered"):
            router.generate("Create a project plan")

    def test_rejects_unapproved_cloud_model(self):
        """Ensure cloud models require explicit approval."""
        cloud_model = ModelConfiguration(
            model_id="cloud-model",
            provider_id="cloud",
            model_name="cloud-model-v1",
            is_local=False,
            requires_approval=True,
        )
        self.registry.register(cloud_model)

        with self.assertRaisesRegex(ValueError, "No eligible model"):
            self.selection_policy.select_model(
                preferred_model_id="cloud-model",
            )

    def test_allows_explicitly_approved_cloud_model(self):
        """Ensure explicitly approved cloud models can be selected."""
        cloud_model = ModelConfiguration(
            model_id="cloud-model",
            provider_id="cloud",
            model_name="cloud-model-v1",
            is_local=False,
            requires_approval=True,
        )
        self.registry.register(cloud_model)

        selected = self.selection_policy.select_model(
            preferred_model_id="cloud-model",
            approved_model_ids=("cloud-model",),
        )

        self.assertEqual(selected.model_id, "cloud-model")

    def test_supports_manual_model_selection(self):
        """Verify the preferred model is selected explicitly."""
        second_model = ModelConfiguration(
            model_id="local-second",
            provider_id="ollama",
            model_name="second-model",
            is_local=True,
        )
        self.registry.register(second_model)

        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={"ollama": self.provider},
            preferred_model_id="local-second",
        )

        router.generate("Use the preferred model")

        self.assertEqual(
            router.last_selected_model_id,
            "local-second",
        )

    def test_rejects_non_string_prompt(self):
        """Ensure prompts must be strings."""
        with self.assertRaises(TypeError):
            self.router.generate(None)

    def test_rejects_empty_prompt(self):
        """Ensure empty prompts are rejected."""
        with self.assertRaises(ValueError):
            self.router.generate("   ")

    def test_rejects_invalid_provider_mapping(self):
        """Ensure provider mappings contain valid provider instances."""
        with self.assertRaises(TypeError):
            ModelRouter(
                registry=self.registry,
                selection_policy=self.selection_policy,
                health_checker=self.health_checker,
                usage_tracker=self.usage_tracker,
                providers={"ollama": object()},
            )

    def test_rejects_mismatched_model_registries(self):
        """Ensure router and selection policy share the same registry."""
        another_registry = ModelRegistry()
        another_policy = ModelSelectionPolicy(another_registry)

        with self.assertRaisesRegex(
            ValueError,
            "Selection policy must use the router's model registry",
        ):
            ModelRouter(
                registry=self.registry,
                selection_policy=another_policy,
                health_checker=self.health_checker,
                usage_tracker=self.usage_tracker,
                providers={"ollama": self.provider},
            )

    def test_rejects_missing_dependencies(self):
        """Ensure required dependencies are validated."""
        with self.assertRaises(TypeError):
            ModelRouter(
                registry=None,
                selection_policy=self.selection_policy,
                health_checker=self.health_checker,
                usage_tracker=self.usage_tracker,
                providers={"ollama": self.provider},
            )


    def test_falls_back_when_first_model_is_unhealthy(self):
        """Verify unhealthy candidates are skipped during fallback."""
        backup_model = ModelConfiguration(
            model_id="local-backup",
            provider_id="ollama",
            model_name="backup-model",
            is_local=True,
            capabilities=("text-generation",),
        )
        self.registry.register(backup_model)
        self.health_check.side_effect = [False, True]

        response = self.router.generate("Test fallback")

        self.assertEqual(response, "Generated response")
        self.assertEqual(
            self.router.last_selected_model_id,
            "local-backup",
        )
        self.assertEqual(self.provider.received_prompts, ["Test fallback"])

    def test_falls_back_when_provider_generation_raises(self):
        """Verify provider errors trigger the next eligible model."""
        class FailingProvider(BaseLLMProvider):
            """Simulate a provider that cannot generate a response."""

            def generate(self, prompt: str) -> str:
                """Raise an error to simulate provider failure."""
                raise RuntimeError("Provider unavailable")

        backup_model = ModelConfiguration(
            model_id="local-backup",
            provider_id="backup",
            model_name="backup-model",
            is_local=True,
            capabilities=("text-generation",),
        )
        self.registry.register(backup_model)

        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={
                "ollama": FailingProvider(),
                "backup": self.provider,
            },
        )

        response = router.generate("Test provider fallback")

        self.assertEqual(response, "Generated response")
        self.assertEqual(
            router.last_selected_model_id,
            "local-backup",
        )
        self.assertEqual(
            self.provider.received_prompts,
            ["Test provider fallback"],
        )


    def test_retries_provider_within_configured_limit(self):
        """Verify generation retries stop after a successful attempt."""
        class SequenceProvider(BaseLLMProvider):
            """Return configured responses in sequence."""

            def __init__(self):
                """Initialize the response sequence and attempt counter."""
                self.attempts = 0

            def generate(self, prompt: str) -> str:
                """Simulate two failures followed by a successful response."""
                self.attempts += 1

                if self.attempts < 3:
                    raise RuntimeError("Temporary provider failure")

                return "Recovered response"

        provider = SequenceProvider()
        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={"ollama": provider},
            max_retries=2,
        )

        response = router.generate("Retry test")

        self.assertEqual(response, "Recovered response")
        self.assertEqual(provider.attempts, 3)
        self.assertEqual(router.last_selected_model_id, "local-qwen")

    def test_stops_after_configured_retry_limit(self):
        """Verify failed generation does not exceed the retry limit."""
        class AlwaysFailingProvider(BaseLLMProvider):
            """Simulate a provider that always fails."""

            def __init__(self):
                """Initialize the attempt counter."""
                self.attempts = 0

            def generate(self, prompt: str) -> str:
                """Raise an error and count each generation attempt."""
                self.attempts += 1
                raise RuntimeError("Provider unavailable")

        provider = AlwaysFailingProvider()
        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={"ollama": provider},
            max_retries=2,
        )

        with self.assertRaisesRegex(RuntimeError, "Provider unavailable"):
            router.generate("Retry limit test")

        self.assertEqual(provider.attempts, 3)
        self.assertEqual(
            self.usage_tracker.get_usage("local-qwen")["request_count"],
            0,
        )


    def test_manual_selection_does_not_fallback_to_another_model(self):
        """Verify manual selection never silently switches models."""
        backup_model = ModelConfiguration(
            model_id="local-backup",
            provider_id="backup",
            model_name="backup-model",
            is_local=True,
            capabilities=("text-generation",),
        )
        self.registry.register(backup_model)

        class FailingProvider(BaseLLMProvider):
            """Simulate failure of the manually selected provider."""

            def generate(self, prompt: str) -> str:
                """Raise an error instead of generating a response."""
                raise RuntimeError("Manual model unavailable")

        backup_provider = FakeProvider()

        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={
                "ollama": FailingProvider(),
                "backup": backup_provider,
            },
            preferred_model_id="local-qwen",
        )

        with self.assertRaisesRegex(RuntimeError, "Manual model unavailable"):
            router.generate("Manual selection test")

        self.assertEqual(backup_provider.received_prompts, [])
        self.assertIsNone(router.last_selected_model_id)


    def test_rejects_negative_max_retries(self):
        """Ensure negative retry limits are rejected."""
        with self.assertRaisesRegex(ValueError, "must not be negative"):
            ModelRouter(
                registry=self.registry,
                selection_policy=self.selection_policy,
                health_checker=self.health_checker,
                usage_tracker=self.usage_tracker,
                providers={"ollama": self.provider},
                max_retries=-1,
            )

    def test_rejects_non_integer_max_retries(self):
        """Ensure non-integer retry limits are rejected."""
        for invalid_value in ("2", 1.5, None):
            with self.subTest(value=invalid_value):
                with self.assertRaises(TypeError):
                    ModelRouter(
                        registry=self.registry,
                        selection_policy=self.selection_policy,
                        health_checker=self.health_checker,
                        usage_tracker=self.usage_tracker,
                        providers={"ollama": self.provider},
                        max_retries=invalid_value,
                    )

    def test_rejects_boolean_max_retries(self):
        """Ensure boolean values are not accepted as retry limits."""
        for invalid_value in (True, False):
            with self.subTest(value=invalid_value):
                with self.assertRaises(TypeError):
                    ModelRouter(
                        registry=self.registry,
                        selection_policy=self.selection_policy,
                        health_checker=self.health_checker,
                        usage_tracker=self.usage_tracker,
                        providers={"ollama": self.provider},
                        max_retries=invalid_value,
                    )


    def test_does_not_retry_generation_when_usage_tracking_fails(self):
        """Ensure usage tracking failures do not repeat successful generation."""
        self.usage_tracker.record_usage = Mock(
            side_effect=RuntimeError("Usage tracking unavailable")
        )

        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={"ollama": self.provider},
            max_retries=2,
        )

        with self.assertRaisesRegex(
            RuntimeError,
            "Usage tracking unavailable",
        ):
            router.generate("Create a project plan")

        self.assertEqual(
            self.provider.received_prompts,
            ["Create a project plan"],
        )


    def test_budget_exceeded_prevents_provider_generation(self):
        """Ensure requests exceeding budget never reach the provider."""
        budget_manager = ModelBudgetManager(
            usage_tracker=self.usage_tracker,
            budget_limits={"local-qwen": 0.0},
        )
        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={"ollama": self.provider},
            budget_manager=budget_manager,
        )

        with self.assertRaises(BudgetExceededError):
            router.generate("Create a project plan")

        self.assertEqual(self.provider.received_prompts, [])
        self.assertEqual(
            self.usage_tracker.get_usage("local-qwen")["request_count"],
            0,
        )

    def test_auto_routing_falls_back_when_model_budget_is_exceeded(self):
        """Ensure automatic routing skips over-budget candidates."""
        backup_model = ModelConfiguration(
            model_id="local-backup",
            provider_id="ollama",
            model_name="backup-model",
            is_local=True,
            capabilities=("text-generation",),
        )
        self.registry.register(backup_model)

        budget_manager = ModelBudgetManager(
            usage_tracker=self.usage_tracker,
            budget_limits={"local-qwen": 0.0},
        )
        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={"ollama": self.provider},
            budget_manager=budget_manager,
        )

        response = router.generate("Use automatic model routing")

        self.assertEqual(response, "Generated response")
        self.assertEqual(router.last_selected_model_id, "local-backup")
        self.assertEqual(
            self.provider.received_prompts,
            ["Use automatic model routing"],
        )

    def test_manual_selection_does_not_fallback_on_budget_exceeded(self):
        """Ensure manual model selection never silently changes models."""
        backup_model = ModelConfiguration(
            model_id="local-backup",
            provider_id="ollama",
            model_name="backup-model",
            is_local=True,
            capabilities=("text-generation",),
        )
        self.registry.register(backup_model)

        budget_manager = ModelBudgetManager(
            usage_tracker=self.usage_tracker,
            budget_limits={"local-qwen": 0.0},
        )
        router = ModelRouter(
            registry=self.registry,
            selection_policy=self.selection_policy,
            health_checker=self.health_checker,
            usage_tracker=self.usage_tracker,
            providers={"ollama": self.provider},
            preferred_model_id="local-qwen",
            budget_manager=budget_manager,
        )

        with self.assertRaises(BudgetExceededError):
            router.generate("Use the manually selected model")

        self.assertEqual(self.provider.received_prompts, [])

    def test_rejects_budget_manager_with_different_usage_tracker(self):
        """Ensure budget and routing calculations share usage history."""
        another_tracker = ModelUsageTracker()
        budget_manager = ModelBudgetManager(
            usage_tracker=another_tracker,
            budget_limits={"local-qwen": 1.0},
        )

        with self.assertRaisesRegex(
            ValueError,
            "Budget manager must use the router's usage tracker",
        ):
            ModelRouter(
                registry=self.registry,
                selection_policy=self.selection_policy,
                health_checker=self.health_checker,
                usage_tracker=self.usage_tracker,
                providers={"ollama": self.provider},
                budget_manager=budget_manager,
            )


if __name__ == "__main__":
    unittest.main()
