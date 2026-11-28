from app.services.llm.model_configuration import ModelConfiguration
from app.services.llm.model_registry import ModelRegistry


class ModelSelectionPolicy:
    """Select eligible models using deterministic selection rules."""

    def __init__(self, registry: ModelRegistry) -> None:
        """Initialize the policy with a model registry."""
        if not isinstance(registry, ModelRegistry):
            raise TypeError("Registry must be a ModelRegistry instance.")

        self._registry = registry

    @property
    def registry(self) -> ModelRegistry:
        """Expose the registry used by this selection policy."""
        return self._registry

    @staticmethod
    def _normalize_capabilities(
        capabilities: tuple[str, ...] | list[str],
    ) -> tuple[str, ...]:
        """Validate and normalize required model capabilities."""
        if not isinstance(capabilities, (tuple, list)):
            raise TypeError("Required capabilities must be a tuple or list.")

        normalized_capabilities = []

        for capability in capabilities:
            if not isinstance(capability, str):
                raise TypeError("Each capability must be a string.")

            normalized_capability = capability.strip().lower()
            if not normalized_capability:
                raise ValueError("Capabilities must not be empty.")

            normalized_capabilities.append(normalized_capability)

        return tuple(normalized_capabilities)

    @staticmethod
    def _is_approved(
        configuration: ModelConfiguration,
        approved_model_ids: tuple[str, ...] | list[str],
    ) -> bool:
        """Check whether a model has explicit approval for use."""
        if not isinstance(approved_model_ids, (tuple, list)):
            raise TypeError("Approved model IDs must be a tuple or list.")

        normalized_ids = []

        for model_id in approved_model_ids:
            if not isinstance(model_id, str):
                raise TypeError("Approved model IDs must be strings.")

            normalized_id = model_id.strip()
            if not normalized_id:
                raise ValueError("Approved model IDs must not be empty.")

            normalized_ids.append(normalized_id)

        if configuration.is_local and not configuration.requires_approval:
            return True

        return configuration.model_id in normalized_ids

    def select_models(
        self,
        required_capabilities: tuple[str, ...] | list[str] = (),
        preferred_model_id: str | None = None,
        approved_model_ids: tuple[str, ...] | list[str] = (),
    ) -> list[ModelConfiguration]:
        """Return all eligible models in deterministic priority order."""
        normalized_capabilities = self._normalize_capabilities(
            required_capabilities
        )

        if preferred_model_id is not None:
            if not isinstance(preferred_model_id, str):
                raise TypeError("Preferred model ID must be a string.")

            normalized_model_id = preferred_model_id.strip()
            if not normalized_model_id:
                raise ValueError("Preferred model ID must not be empty.")

            configuration = self._registry.get(normalized_model_id)

            if configuration is None:
                raise ValueError(
                    f"Model '{normalized_model_id}' is not registered."
                )

            candidates = [configuration]
        else:
            candidates = self._registry.list_enabled_models()

        eligible_models = []

        for configuration in candidates:
            if not configuration.enabled:
                continue

            model_capabilities = {
                capability.lower()
                for capability in configuration.capabilities
            }

            if not set(normalized_capabilities).issubset(
                model_capabilities
            ):
                continue

            if not self._is_approved(
                configuration,
                approved_model_ids,
            ):
                continue

            eligible_models.append(configuration)

        if not eligible_models:
            raise ValueError("No eligible model is available.")

        if preferred_model_id is not None:
            return eligible_models

        # Prioritize local models while preserving registry order.
        local_models = [
            configuration
            for configuration in eligible_models
            if configuration.is_local
        ]
        cloud_models = [
            configuration
            for configuration in eligible_models
            if not configuration.is_local
        ]

        return local_models + cloud_models

    def select_model(
        self,
        required_capabilities: tuple[str, ...] | list[str] = (),
        preferred_model_id: str | None = None,
        approved_model_ids: tuple[str, ...] | list[str] = (),
    ) -> ModelConfiguration:
        """Select the highest-priority eligible model."""
        return self.select_models(
            required_capabilities=required_capabilities,
            preferred_model_id=preferred_model_id,
            approved_model_ids=approved_model_ids,
        )[0]
