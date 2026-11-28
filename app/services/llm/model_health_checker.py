from collections.abc import Callable

from app.services.llm.model_configuration import ModelConfiguration


class ModelHealthChecker:
    """Check model availability through an injected health-check callback."""

    def __init__(
        self,
        health_check: Callable[[ModelConfiguration], bool],
    ) -> None:
        """Initialize the checker with a health-check callback."""
        if not callable(health_check):
            raise TypeError("Health check must be callable.")

        self._health_check = health_check

    def check(self, configuration: ModelConfiguration) -> bool:
        """Return whether the configured model is currently healthy."""
        if not isinstance(configuration, ModelConfiguration):
            raise TypeError(
                "Configuration must be a ModelConfiguration instance."
            )

        if not configuration.enabled:
            return False

        try:
            result = self._health_check(configuration)
        except Exception:
            return False

        if not isinstance(result, bool):
            raise TypeError("Health check must return a boolean.")

        return result
