from app.services.llm.model_configuration import ModelConfiguration


class ModelRegistry:
    """Manage model configuration registration and lookup."""

    def __init__(self) -> None:
        """Initialize an empty model registry."""
        self._models: dict[str, ModelConfiguration] = {}

    def register(self, configuration: ModelConfiguration) -> None:
        """Register a model configuration using its stable identifier."""
        if not isinstance(configuration, ModelConfiguration):
            raise TypeError(
                "Only ModelConfiguration instances can be registered."
            )

        if configuration.model_id in self._models:
            raise ValueError(
                f"Model ID '{configuration.model_id}' is already registered."
            )

        self._models[configuration.model_id] = configuration

    @staticmethod
    def _validate_model_id(model_id: str) -> str:
        """Validate and normalize a model identifier."""
        if not isinstance(model_id, str):
            raise TypeError("Model ID must be a string.")

        normalized_id = model_id.strip()
        if not normalized_id:
            raise ValueError("Model ID must not be empty.")

        return normalized_id

    def get(self, model_id: str) -> ModelConfiguration | None:
        """Retrieve a model configuration by its stable identifier."""
        normalized_id = self._validate_model_id(model_id)
        return self._models.get(normalized_id)

    def unregister(self, model_id: str) -> ModelConfiguration | None:
        """Remove and return a model configuration by its identifier."""
        normalized_id = self._validate_model_id(model_id)
        return self._models.pop(normalized_id, None)

    def list_models(self) -> list[ModelConfiguration]:
        """Return all registered model configurations in insertion order."""
        return list(self._models.values())

    def list_enabled_models(self) -> list[ModelConfiguration]:
        """Return only enabled model configurations."""
        return [
            configuration
            for configuration in self._models.values()
            if configuration.enabled
        ]

    def get_by_provider(
        self,
        provider_id: str,
    ) -> list[ModelConfiguration]:
        """Return model configurations belonging to a provider."""
        if not isinstance(provider_id, str):
            raise TypeError("Provider ID must be a string.")

        normalized_id = provider_id.strip().lower()
        if not normalized_id:
            raise ValueError("Provider ID must not be empty.")

        return [
            configuration
            for configuration in self._models.values()
            if configuration.provider_id.lower() == normalized_id
        ]
