from app.services.llm.base_provider import BaseLLMProvider
from app.services.llm.model_budget_manager import (
    BudgetExceededError,
    ModelBudgetManager,
)
from app.services.llm.model_health_checker import ModelHealthChecker
from app.services.llm.model_registry import ModelRegistry
from app.services.llm.model_selection_policy import ModelSelectionPolicy
from app.services.llm.model_usage_tracker import ModelUsageTracker
from app.utils.token_estimator import estimate_tokens


class ModelRouter(BaseLLMProvider):
    """Route text generation requests to eligible LLM providers."""

    def __init__(
        self,
        registry: ModelRegistry,
        selection_policy: ModelSelectionPolicy,
        health_checker: ModelHealthChecker,
        usage_tracker: ModelUsageTracker,
        providers: dict[str, BaseLLMProvider],
        preferred_model_id: str | None = None,
        approved_model_ids: tuple[str, ...] | list[str] = (),
        required_capabilities: tuple[str, ...] | list[str] = (),
        max_retries: int = 0,
        budget_manager: ModelBudgetManager | None = None,
        max_output_tokens: int = 512,
    ) -> None:
        """Initialize the router with injected routing dependencies."""
        super().__init__()

        # Validate required routing dependencies.
        dependencies = (
            ("Registry", registry, ModelRegistry),
            ("Selection policy", selection_policy, ModelSelectionPolicy),
            ("Health checker", health_checker, ModelHealthChecker),
            ("Usage tracker", usage_tracker, ModelUsageTracker),
        )

        for name, dependency, expected_type in dependencies:
            if not isinstance(dependency, expected_type):
                raise TypeError(
                    f"{name} must be a {expected_type.__name__} instance."
                )

        # Ensure routing and selection use the same model registry.
        if selection_policy.registry is not registry:
            raise ValueError(
                "Selection policy must use the router's model registry."
            )

        if not isinstance(providers, dict):
            raise TypeError("Providers must be a dictionary.")

        # Validate and normalize provider registrations.
        normalized_providers = {}

        for provider_id, provider in providers.items():
            if not isinstance(provider_id, str):
                raise TypeError("Provider IDs must be strings.")

            normalized_id = provider_id.strip().lower()
            if not normalized_id:
                raise ValueError("Provider IDs must not be empty.")

            if not isinstance(provider, BaseLLMProvider):
                raise TypeError(
                    "Every registered provider must implement BaseLLMProvider."
                )

            if normalized_id in normalized_providers:
                raise ValueError(
                    f"Provider ID '{normalized_id}' is duplicated."
                )

            normalized_providers[normalized_id] = provider

        # Validate optional model selection settings.
        if preferred_model_id is not None:
            if not isinstance(preferred_model_id, str):
                raise TypeError("Preferred model ID must be a string.")

            preferred_model_id = preferred_model_id.strip()
            if not preferred_model_id:
                raise ValueError("Preferred model ID must not be empty.")

        if not isinstance(approved_model_ids, (tuple, list)):
            raise TypeError("Approved model IDs must be a tuple or list.")

        if not isinstance(required_capabilities, (tuple, list)):
            raise TypeError("Required capabilities must be a tuple or list.")

        if isinstance(max_retries, bool) or not isinstance(max_retries, int):
            raise TypeError("Maximum retries must be an integer.")

        if max_retries < 0:
            raise ValueError("Maximum retries must not be negative.")

        if budget_manager is not None and not isinstance(
            budget_manager, ModelBudgetManager
        ):
            raise TypeError(
                "Budget manager must be a ModelBudgetManager instance."
            )

        if (
            budget_manager is not None
            and budget_manager.usage_tracker is not usage_tracker
        ):
            raise ValueError(
                "Budget manager must use the router's usage tracker."
            )

        if isinstance(max_output_tokens, bool) or not isinstance(
            max_output_tokens, int
        ):
            raise TypeError("Maximum output tokens must be an integer.")

        if max_output_tokens <= 0:
            raise ValueError(
                "Maximum output tokens must be greater than zero."
            )

        # Store normalized routing dependencies and configuration.
        self._registry = registry
        self._selection_policy = selection_policy
        self._health_checker = health_checker
        self._usage_tracker = usage_tracker
        self._providers = normalized_providers
        self._preferred_model_id = preferred_model_id
        self._approved_model_ids = tuple(approved_model_ids)
        self._required_capabilities = tuple(required_capabilities)
        self._max_retries = max_retries
        self._budget_manager = budget_manager
        self._max_output_tokens = max_output_tokens

        # Track the most recently successful model for diagnostics.
        self.last_selected_model_id: str | None = None

    def generate(self, prompt: str) -> str:
        """Generate text using ordered candidates with bounded retries."""
        # Validate the generation request before selecting a model.
        if not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")
        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        # Clear previous success metadata for the new valid request.
        self.last_selected_model_id = None

        # Retrieve eligible candidates while enforcing approval rules.
        configurations = self._selection_policy.select_models(
            required_capabilities=self._required_capabilities,
            preferred_model_id=self._preferred_model_id,
            approved_model_ids=self._approved_model_ids,
        )
        last_error = None

        # Try each eligible candidate in deterministic priority order.
        for configuration in configurations:
            if not self._health_checker.check(configuration):
                last_error = RuntimeError(
                    f"Model '{configuration.model_id}' is unhealthy."
                )
                continue

            provider_id = configuration.provider_id.strip().lower()
            provider = self._providers.get(provider_id)
            if provider is None:
                last_error = RuntimeError(
                    f"No provider registered for '{configuration.provider_id}'."
                )
                continue

            # Enforce the configured model budget before provider generation.
            if self._budget_manager is not None:
                try:
                    self._budget_manager.check_request(
                        configuration=configuration,
                        prompt=prompt,
                        max_output_tokens=self._max_output_tokens,
                    )
                except BudgetExceededError as error:
                    if self._preferred_model_id is not None:
                        raise

                    last_error = error
                    continue

            response = None

            # Retry only provider generation and response validation.
            for _ in range(self._max_retries + 1):
                try:
                    generated_response = provider.generate(prompt)
                    if (
                        not isinstance(generated_response, str)
                        or not generated_response.strip()
                    ):
                        raise RuntimeError(
                            "LLM provider must return a non-empty string."
                        )
                    response = generated_response.strip()
                    break
                except Exception as error:
                    last_error = error

            if response is None:
                continue

            # Record the successful model before updating usage telemetry.
            self.last_selected_model_id = configuration.model_id

            # Usage tracking failures must not trigger another generation.
            self._usage_tracker.record_usage(
                configuration=configuration,
                input_tokens=estimate_tokens(prompt),
                output_tokens=estimate_tokens(response),
            )
            return response

        # Report the final failure if every eligible candidate failed.
        if last_error is not None:
            raise last_error
        raise RuntimeError("No eligible model could generate a response.")
