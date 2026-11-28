import unittest

from app.services.llm.model_configuration import ModelConfiguration
from app.services.llm.model_registry import ModelRegistry
from app.services.llm.model_selection_policy import ModelSelectionPolicy


class TestModelSelectionPolicy(unittest.TestCase):
    """Test model eligibility and selection behavior."""

    def setUp(self) -> None:
        """Initialize a registry with local and cloud models."""
        self.registry = ModelRegistry()
        self.local_model = ModelConfiguration(
            model_id="local-model",
            provider_id="ollama",
            model_name="qwen2.5:0.5b",
            capabilities=("text", "chat"),
            is_local=True,
        )
        self.cloud_model = ModelConfiguration(
            model_id="cloud-model",
            provider_id="gemini",
            model_name="gemini-model",
            capabilities=("text", "chat"),
            requires_approval=True,
        )
        self.disabled_model = ModelConfiguration(
            model_id="disabled-model",
            provider_id="ollama",
            model_name="disabled-model",
            enabled=False,
            capabilities=("text", "chat"),
            is_local=True,
        )

        self.registry.register(self.local_model)
        self.registry.register(self.cloud_model)
        self.registry.register(self.disabled_model)

        self.policy = ModelSelectionPolicy(self.registry)

    def test_prefers_local_model_automatically(self) -> None:
        """Verify automatic selection prefers an eligible local model."""
        selected = self.policy.select_model()

        self.assertIs(selected, self.local_model)

    def test_cloud_model_requires_approval(self) -> None:
        """Verify cloud models are excluded without explicit approval."""
        registry = ModelRegistry()
        registry.register(self.cloud_model)
        policy = ModelSelectionPolicy(registry)

        with self.assertRaises(ValueError):
            policy.select_model()

    def test_selects_approved_cloud_model(self) -> None:
        """Verify an explicitly approved cloud model can be selected."""
        registry = ModelRegistry()
        registry.register(self.cloud_model)
        policy = ModelSelectionPolicy(registry)

        selected = policy.select_model(
            approved_model_ids=("cloud-model",)
        )

        self.assertIs(selected, self.cloud_model)

    def test_manual_selection_uses_requested_model(self) -> None:
        """Verify preferred model selection returns the requested model."""
        selected = self.policy.select_model(
            preferred_model_id="cloud-model",
            approved_model_ids=("cloud-model",),
        )

        self.assertIs(selected, self.cloud_model)

    def test_manual_selection_rejects_unknown_model(self) -> None:
        """Verify unknown preferred models are rejected."""
        with self.assertRaises(ValueError):
            self.policy.select_model(
                preferred_model_id="unknown-model"
            )

    def test_manual_selection_rejects_disabled_model(self) -> None:
        """Verify disabled models cannot be selected manually."""
        with self.assertRaises(ValueError):
            self.policy.select_model(
                preferred_model_id="disabled-model"
            )

    def test_filters_by_required_capabilities(self) -> None:
        """Verify models must support all requested capabilities."""
        selected = self.policy.select_model(
            required_capabilities=(" CHAT ",)
        )

        self.assertIs(selected, self.local_model)

        with self.assertRaises(ValueError):
            self.policy.select_model(
                required_capabilities=("vision",)
            )

    def test_returns_error_when_no_model_is_eligible(self) -> None:
        """Verify selection fails when no eligible model exists."""
        registry = ModelRegistry()
        policy = ModelSelectionPolicy(registry)

        with self.assertRaises(ValueError):
            policy.select_model()

    def test_validates_required_capabilities(self) -> None:
        """Verify required capability values are validated."""
        with self.assertRaises(TypeError):
            self.policy.select_model(required_capabilities="text")

        with self.assertRaises(TypeError):
            self.policy.select_model(
                required_capabilities=(123,)
            )

        with self.assertRaises(ValueError):
            self.policy.select_model(
                required_capabilities=(" ",)
            )

    def test_validates_approved_model_ids(self) -> None:
        """Verify approval identifiers are validated."""
        with self.assertRaises(TypeError):
            self.policy.select_model(
                approved_model_ids="cloud-model"
            )

        with self.assertRaises(TypeError):
            self.policy.select_model(
                approved_model_ids=(123,)
            )

        with self.assertRaises(ValueError):
            self.policy.select_model(
                approved_model_ids=(" ",)
            )

    def test_validates_preferred_model_id(self) -> None:
        """Verify preferred model identifiers are validated."""
        with self.assertRaises(TypeError):
            self.policy.select_model(preferred_model_id=123)

        with self.assertRaises(ValueError):
            self.policy.select_model(preferred_model_id=" ")

    def test_rejects_invalid_registry(self) -> None:
        """Verify the policy requires a ModelRegistry instance."""
        with self.assertRaises(TypeError):
            ModelSelectionPolicy("invalid")


    def test_select_models_returns_local_first_and_approved_cloud_models(self) -> None:
        """Verify eligible models are ordered with local models first."""
        selected = self.policy.select_models(
            approved_model_ids=("cloud-model",)
        )

        self.assertEqual(
            [model.model_id for model in selected],
            ["local-model", "cloud-model"],
        )

    def test_select_models_preserves_manual_model_selection(self) -> None:
        """Verify manual selection returns only the requested model."""
        selected = self.policy.select_models(
            preferred_model_id="cloud-model",
            approved_model_ids=("cloud-model",),
        )

        self.assertEqual(
            [model.model_id for model in selected],
            ["cloud-model"],
        )

    def test_select_models_excludes_unapproved_and_disabled_models(self) -> None:
        """Verify ineligible models are excluded from the candidate list."""
        selected = self.policy.select_models()

        self.assertEqual(
            [model.model_id for model in selected],
            ["local-model"],
        )


if __name__ == "__main__":
    unittest.main()
