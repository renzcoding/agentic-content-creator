import unittest

from app.services.llm.model_configuration import ModelConfiguration
from app.services.llm.model_usage_tracker import ModelUsageTracker


class TestModelUsageTracker(unittest.TestCase):
    """Test model usage aggregation and cost estimation."""

    def setUp(self) -> None:
        """Initialize a tracker and priced model configuration."""
        self.tracker = ModelUsageTracker()
        self.configuration = ModelConfiguration(
            model_id="priced-model",
            provider_id="test-provider",
            model_name="test-model",
            input_cost_per_1k_tokens=0.002,
            output_cost_per_1k_tokens=0.004,
        )

    def test_records_request_and_token_usage(self) -> None:
        """Verify request and token totals are recorded."""
        usage = self.tracker.record_usage(
            self.configuration,
            input_tokens=100,
            output_tokens=50,
        )

        self.assertEqual(usage["request_count"], 1)
        self.assertEqual(usage["input_tokens"], 100)
        self.assertEqual(usage["output_tokens"], 50)

    def test_calculates_estimated_cost(self) -> None:
        """Verify estimated cost uses per-1K token pricing."""
        usage = self.tracker.record_usage(
            self.configuration,
            input_tokens=500,
            output_tokens=250,
        )

        self.assertAlmostEqual(usage["estimated_cost"], 0.002)

    def test_accumulates_multiple_requests(self) -> None:
        """Verify usage totals accumulate across requests."""
        self.tracker.record_usage(
            self.configuration,
            input_tokens=500,
            output_tokens=250,
        )
        usage = self.tracker.record_usage(
            self.configuration,
            input_tokens=500,
            output_tokens=250,
        )

        self.assertEqual(usage["request_count"], 2)
        self.assertEqual(usage["input_tokens"], 1000)
        self.assertEqual(usage["output_tokens"], 500)
        self.assertAlmostEqual(usage["estimated_cost"], 0.004)

    def test_unknown_pricing_returns_none_cost(self) -> None:
        """Verify incomplete pricing is not treated as free."""
        configuration = ModelConfiguration(
            model_id="unknown-price-model",
            provider_id="test-provider",
            model_name="unknown-price-model",
        )

        usage = self.tracker.record_usage(
            configuration,
            input_tokens=100,
            output_tokens=50,
        )

        self.assertIsNone(usage["estimated_cost"])

    def test_cost_remains_unknown_after_incomplete_pricing(self) -> None:
        """Verify unknown historical pricing is not later estimated."""
        unknown_configuration = ModelConfiguration(
            model_id="changing-price-model",
            provider_id="test-provider",
            model_name="changing-price-model",
        )
        priced_configuration = ModelConfiguration(
            model_id="changing-price-model",
            provider_id="test-provider",
            model_name="changing-price-model",
            input_cost_per_1k_tokens=0.002,
            output_cost_per_1k_tokens=0.004,
        )

        self.tracker.record_usage(
            unknown_configuration,
            input_tokens=100,
            output_tokens=50,
        )
        usage = self.tracker.record_usage(
            priced_configuration,
            input_tokens=100,
            output_tokens=50,
        )

        self.assertIsNone(usage["estimated_cost"])

    def test_returns_zero_usage_for_unknown_model(self) -> None:
        """Verify unknown models return zero usage."""
        usage = self.tracker.get_usage("unknown-model")

        self.assertEqual(usage["request_count"], 0)
        self.assertEqual(usage["input_tokens"], 0)
        self.assertEqual(usage["output_tokens"], 0)
        self.assertEqual(usage["estimated_cost"], 0.0)

    def test_returns_copy_of_usage(self) -> None:
        """Verify returned usage cannot mutate internal statistics."""
        self.tracker.record_usage(
            self.configuration,
            input_tokens=100,
            output_tokens=50,
        )

        usage = self.tracker.get_usage("priced-model")
        usage["input_tokens"] = 9999

        self.assertEqual(
            self.tracker.get_usage("priced-model")["input_tokens"],
            100,
        )

    def test_lists_usage_for_all_models(self) -> None:
        """Verify usage can be retrieved for all tracked models."""
        self.tracker.record_usage(
            self.configuration,
            input_tokens=100,
            output_tokens=50,
        )

        usage = self.tracker.list_usage()

        self.assertIn("priced-model", usage)
        self.assertEqual(usage["priced-model"]["request_count"], 1)

    def test_rejects_invalid_configuration(self) -> None:
        """Verify usage recording requires a model configuration."""
        with self.assertRaises(TypeError):
            self.tracker.record_usage("invalid", 10, 5)

    def test_validates_token_counts(self) -> None:
        """Verify token counts must be non-negative integers."""
        with self.assertRaises(TypeError):
            self.tracker.record_usage(
                self.configuration,
                input_tokens=True,
                output_tokens=10,
            )

        with self.assertRaises(TypeError):
            self.tracker.record_usage(
                self.configuration,
                input_tokens=10,
                output_tokens=1.5,
            )

        with self.assertRaises(ValueError):
            self.tracker.record_usage(
                self.configuration,
                input_tokens=-1,
                output_tokens=10,
            )

    def test_validates_model_id_for_lookup(self) -> None:
        """Verify model IDs are validated when retrieving usage."""
        with self.assertRaises(TypeError):
            self.tracker.get_usage(123)

        with self.assertRaises(ValueError):
            self.tracker.get_usage(" ")


if __name__ == "__main__":
    unittest.main()
