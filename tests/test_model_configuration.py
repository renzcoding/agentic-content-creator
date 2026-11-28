import unittest
from math import inf, nan

from app.services.llm.model_configuration import ModelConfiguration


class TestModelConfiguration(unittest.TestCase):
    """Test model metadata validation and access."""

    def setUp(self):
        """Create a valid model configuration for testing."""
        self.configuration = ModelConfiguration(
            model_id=" ollama/qwen2.5:0.5b ",
            provider_id=" ollama ",
            model_name=" qwen2.5:0.5b ",
            capabilities=(" text-generation ", "chat"),
            context_window=2048,
            is_local=True,
        )

    def test_normalizes_model_identifiers(self):
        """Verify that model identifiers are trimmed."""
        self.assertEqual(
            self.configuration.model_id,
            "ollama/qwen2.5:0.5b",
        )
        self.assertEqual(self.configuration.provider_id, "ollama")
        self.assertEqual(self.configuration.model_name, "qwen2.5:0.5b")

    def test_uses_valid_default_values(self):
        """Verify default model configuration values."""
        configuration = ModelConfiguration(
            "provider/model",
            "provider",
            "model",
        )

        self.assertTrue(configuration.enabled)
        self.assertEqual(configuration.capabilities, ())
        self.assertIsNone(configuration.context_window)
        self.assertFalse(configuration.is_local)
        self.assertFalse(configuration.requires_approval)
        self.assertIsNone(configuration.input_cost_per_1k_tokens)
        self.assertIsNone(configuration.output_cost_per_1k_tokens)

    def test_normalizes_capabilities_to_immutable_tuple(self):
        """Verify capabilities are normalized and stored as a tuple."""
        self.assertEqual(
            self.configuration.capabilities,
            ("text-generation", "chat"),
        )
        self.assertIsInstance(self.configuration.capabilities, tuple)

    def test_rejects_empty_identifiers(self):
        """Verify empty identifiers are rejected."""
        for field_name in ("model_id", "provider_id", "model_name"):
            values = {
                "model_id": "model",
                "provider_id": "provider",
                "model_name": "name",
            }
            values[field_name] = " "

            with self.subTest(field=field_name):
                with self.assertRaises(ValueError):
                    ModelConfiguration(**values)

    def test_rejects_non_string_identifiers(self):
        """Verify identifiers must be strings."""
        for field_name in ("model_id", "provider_id", "model_name"):
            values = {
                "model_id": "model",
                "provider_id": "provider",
                "model_name": "name",
            }
            values[field_name] = None

            with self.subTest(field=field_name):
                with self.assertRaises(TypeError):
                    ModelConfiguration(**values)

    def test_rejects_non_boolean_flags(self):
        """Verify boolean configuration flags reject other types."""
        for field_name in ("enabled", "is_local", "requires_approval"):
            with self.subTest(field=field_name):
                with self.assertRaises(TypeError):
                    ModelConfiguration(
                        "provider/model",
                        "provider",
                        "model",
                        **{field_name: 1},
                    )

    def test_rejects_invalid_capabilities(self):
        """Verify capability collections and values are validated."""
        with self.assertRaises(TypeError):
            ModelConfiguration(
                "provider/model",
                "provider",
                "model",
                capabilities="chat",
            )

        with self.assertRaises(ValueError):
            ModelConfiguration(
                "provider/model",
                "provider",
                "model",
                capabilities=(" ",),
            )

    def test_rejects_invalid_context_window(self):
        """Verify context window must be a positive integer."""
        for value in (0, -1):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ModelConfiguration(
                        "provider/model",
                        "provider",
                        "model",
                        context_window=value,
                    )

        for value in (True, 2048.0, "2048"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    ModelConfiguration(
                        "provider/model",
                        "provider",
                        "model",
                        context_window=value,
                    )

    def test_accepts_non_negative_costs(self):
        """Verify zero and positive model costs are accepted."""
        configuration = ModelConfiguration(
            "provider/model",
            "provider",
            "model",
            input_cost_per_1k_tokens=0,
            output_cost_per_1k_tokens=0.25,
        )

        self.assertEqual(configuration.input_cost_per_1k_tokens, 0.0)
        self.assertEqual(configuration.output_cost_per_1k_tokens, 0.25)

    def test_rejects_negative_costs(self):
        """Verify negative model costs are rejected."""
        for field_name in (
            "input_cost_per_1k_tokens",
            "output_cost_per_1k_tokens",
        ):
            with self.subTest(field=field_name):
                with self.assertRaises(ValueError):
                    ModelConfiguration(
                        "provider/model",
                        "provider",
                        "model",
                        **{field_name: -0.01},
                    )

    def test_rejects_non_numeric_costs(self):
        """Verify model costs must be numeric when supplied."""
        for value in (True, "0.1"):
            with self.subTest(value=value):
                with self.assertRaises(TypeError):
                    ModelConfiguration(
                        "provider/model",
                        "provider",
                        "model",
                        input_cost_per_1k_tokens=value,
                    )

    def test_rejects_non_finite_costs(self):
        """Verify NaN and infinite model costs are rejected."""
        for value in (nan, inf, -inf):
            with self.subTest(value=value):
                with self.assertRaises(ValueError):
                    ModelConfiguration(
                        "provider/model",
                        "provider",
                        "model",
                        input_cost_per_1k_tokens=value,
                    )


if __name__ == "__main__":
    unittest.main()
