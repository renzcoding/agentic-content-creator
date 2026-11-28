import unittest

from app.services.llm.model_configuration import ModelConfiguration
from app.services.llm.model_registry import ModelRegistry


class TestModelRegistry(unittest.TestCase):
    """Test model registration, lookup, filtering, and removal."""

    def setUp(self) -> None:
        """Initialize a registry and sample model configurations."""
        self.registry = ModelRegistry()
        self.local_model = ModelConfiguration(
            model_id="local-model",
            provider_id="ollama",
            model_name="qwen2.5:0.5b",
            is_local=True,
        )
        self.disabled_model = ModelConfiguration(
            model_id="disabled-model",
            provider_id="ollama",
            model_name="qwen2.5:1.5b",
            enabled=False,
            is_local=True,
        )
        self.cloud_model = ModelConfiguration(
            model_id="cloud-model",
            provider_id="gemini",
            model_name="gemini-model",
            requires_approval=True,
        )

    def test_registers_and_retrieves_model(self) -> None:
        """Verify a registered model can be retrieved by its ID."""
        self.registry.register(self.local_model)

        self.assertIs(
            self.registry.get("local-model"),
            self.local_model,
        )

    def test_rejects_invalid_configuration(self) -> None:
        """Verify only ModelConfiguration instances can be registered."""
        with self.assertRaises(TypeError):
            self.registry.register("invalid")

    def test_rejects_duplicate_model_id(self) -> None:
        """Verify duplicate model identifiers are rejected."""
        self.registry.register(self.local_model)

        with self.assertRaises(ValueError):
            self.registry.register(self.local_model)

    def test_get_returns_none_for_unknown_model(self) -> None:
        """Verify lookup returns None for an unknown model."""
        self.assertIsNone(self.registry.get("unknown-model"))

    def test_validates_model_id(self) -> None:
        """Verify model identifiers are validated and normalized."""
        with self.assertRaises(TypeError):
            self.registry.get(123)

        with self.assertRaises(ValueError):
            self.registry.get(" ")

        self.registry.register(self.local_model)
        self.assertIs(
            self.registry.get(" local-model "),
            self.local_model,
        )

    def test_unregisters_model(self) -> None:
        """Verify unregister removes and returns a model."""
        self.registry.register(self.local_model)

        removed = self.registry.unregister("local-model")

        self.assertIs(removed, self.local_model)
        self.assertIsNone(self.registry.get("local-model"))

    def test_unregister_returns_none_for_unknown_model(self) -> None:
        """Verify unregister returns None when the model is absent."""
        self.assertIsNone(self.registry.unregister("unknown-model"))

    def test_lists_models_in_registration_order(self) -> None:
        """Verify registered models are returned in insertion order."""
        self.registry.register(self.local_model)
        self.registry.register(self.cloud_model)

        self.assertEqual(
            self.registry.list_models(),
            [self.local_model, self.cloud_model],
        )

    def test_lists_enabled_models_only(self) -> None:
        """Verify disabled models are excluded from enabled model listing."""
        self.registry.register(self.local_model)
        self.registry.register(self.disabled_model)

        self.assertEqual(
            self.registry.list_enabled_models(),
            [self.local_model],
        )

    def test_filters_models_by_provider(self) -> None:
        """Verify models can be filtered by provider identifier."""
        self.registry.register(self.local_model)
        self.registry.register(self.disabled_model)
        self.registry.register(self.cloud_model)

        self.assertEqual(
            self.registry.get_by_provider(" OLLAMA "),
            [self.local_model, self.disabled_model],
        )

    def test_validates_provider_id(self) -> None:
        """Verify provider identifiers are validated."""
        with self.assertRaises(TypeError):
            self.registry.get_by_provider(123)

        with self.assertRaises(ValueError):
            self.registry.get_by_provider(" ")

    def test_returns_empty_list_for_unknown_provider(self) -> None:
        """Verify unknown providers return an empty list."""
        self.assertEqual(
            self.registry.get_by_provider("unknown-provider"),
            [],
        )


if __name__ == "__main__":
    unittest.main()
