import unittest

from app.services.llm.model_budget_manager import (
    BudgetExceededError,
    ModelBudgetManager,
)
from app.services.llm.model_configuration import ModelConfiguration
from app.services.llm.model_usage_tracker import ModelUsageTracker


class TestModelBudgetManager(unittest.TestCase):
    """Test pre-generation model budget checks."""

    def setUp(self):
        """Initialize a priced model and usage tracker."""
        self.configuration = ModelConfiguration(
            model_id="budget-model",
            provider_id="test-provider",
            model_name="test-model",
            input_cost_per_1k_tokens=0.002,
            output_cost_per_1k_tokens=0.004,
        )
        self.tracker = ModelUsageTracker()
        self.manager = ModelBudgetManager(
            usage_tracker=self.tracker,
            budget_limits={"budget-model": 1.0},
        )

    def test_allows_request_within_budget(self):
        """Allow a request whose estimated total remains under budget."""
        estimated_cost = self.manager.check_request(
            self.configuration,
            prompt="Test prompt",
            max_output_tokens=100,
        )

        self.assertGreaterEqual(estimated_cost, 0.0)

    def test_rejects_request_exceeding_budget(self):
        """Reject a request when its estimated cost exceeds the limit."""
        manager = ModelBudgetManager(
            usage_tracker=self.tracker,
            budget_limits={"budget-model": 0.0001},
        )

        with self.assertRaises(BudgetExceededError):
            manager.check_request(
                self.configuration,
                prompt="A longer prompt for budget testing",
                max_output_tokens=1000,
            )

    def test_accounts_for_previous_usage(self):
        """Include previously recorded estimated cost in the budget."""
        self.tracker.record_usage(
            self.configuration,
            input_tokens=1000,
            output_tokens=1000,
        )

        manager = ModelBudgetManager(
            usage_tracker=self.tracker,
            budget_limits={"budget-model": 0.005},
        )

        with self.assertRaises(BudgetExceededError):
            manager.check_request(
                self.configuration,
                prompt="Another request",
                max_output_tokens=100,
            )

    def test_rejects_unknown_pricing_when_budget_is_configured(self):
        """Do not treat missing model pricing as free."""
        configuration = ModelConfiguration(
            model_id="unknown-price",
            provider_id="test-provider",
            model_name="unknown-price",
        )
        manager = ModelBudgetManager(
            usage_tracker=self.tracker,
            budget_limits={"unknown-price": 1.0},
        )

        with self.assertRaisesRegex(ValueError, "pricing must be configured"):
            manager.check_request(
                configuration,
                prompt="Test prompt",
                max_output_tokens=100,
            )

    def test_rejects_unknown_historical_cost(self):
        """Reject budget enforcement when previous cost is unknown."""
        unknown_pricing_configuration = ModelConfiguration(
            model_id="budget-model",
            provider_id="test-provider",
            model_name="test-model",
        )
        self.tracker.record_usage(
            unknown_pricing_configuration,
            input_tokens=100,
            output_tokens=50,
        )

        manager = ModelBudgetManager(
            usage_tracker=self.tracker,
            budget_limits={"budget-model": 1.0},
        )

        with self.assertRaises(BudgetExceededError):
            manager.check_request(
                self.configuration,
                prompt="Test prompt",
                max_output_tokens=100,
            )

    def test_allows_model_without_configured_budget(self):
        """Return None when no budget limit is configured for a model."""
        manager = ModelBudgetManager(
            usage_tracker=self.tracker,
            budget_limits={},
        )

        result = manager.check_request(
            self.configuration,
            prompt="Test prompt",
            max_output_tokens=100,
        )

        self.assertIsNone(result)

    def test_rejects_invalid_output_token_limit(self):
        """Require a positive integer output token limit."""
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    self.manager.check_request(
                        self.configuration,
                        prompt="Test prompt",
                        max_output_tokens=value,
                    )

        with self.assertRaises(TypeError):
            self.manager.check_request(
                self.configuration,
                prompt="Test prompt",
                max_output_tokens=True,
            )

    def test_rejects_invalid_budget_limit(self):
        """Reject negative and non-finite budget values."""
        for value in (-1, float("inf"), float("nan")):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ModelBudgetManager(
                        usage_tracker=self.tracker,
                        budget_limits={"budget-model": value},
                    )


if __name__ == "__main__":
    unittest.main()
