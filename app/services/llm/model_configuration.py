from math import isfinite


class ModelConfiguration:
    """Store validated metadata for one LLM model."""

    def __init__(
        self,
        model_id: str,
        provider_id: str,
        model_name: str,
        enabled: bool = True,
        capabilities: tuple[str, ...] = (),
        context_window: int | None = None,
        is_local: bool = False,
        requires_approval: bool = False,
        input_cost_per_1k_tokens: float | None = None,
        output_cost_per_1k_tokens: float | None = None,
    ) -> None:
        """Initialize and validate model metadata."""
        # Validate and normalize the model identifiers.
        self._model_id = self._validate_identifier(model_id, "Model ID")
        self._provider_id = self._validate_identifier(provider_id, "Provider ID")
        self._model_name = self._validate_identifier(model_name, "Model name")

        # Validate boolean configuration flags.
        for field_name, value in (
            ("Enabled", enabled),
            ("Is local", is_local),
            ("Requires approval", requires_approval),
        ):
            if not isinstance(value, bool):
                raise TypeError(f"{field_name} must be a boolean.")

        # Validate and normalize model capabilities.
        if not isinstance(capabilities, (tuple, list)):
            raise TypeError("Capabilities must be a tuple or list.")

        normalized_capabilities = []
        for capability in capabilities:
            normalized_capabilities.append(
                self._validate_identifier(capability, "Capability")
            )

        # Validate the optional context window.
        if context_window is not None:
            if isinstance(context_window, bool) or not isinstance(
                context_window, int
            ):
                raise TypeError("Context window must be an integer.")

            if context_window <= 0:
                raise ValueError("Context window must be greater than zero.")

        # Validate optional model pricing metadata.
        input_cost = self._validate_cost(
            input_cost_per_1k_tokens,
            "Input cost",
        )
        output_cost = self._validate_cost(
            output_cost_per_1k_tokens,
            "Output cost",
        )

        # Store validated values using private attributes.
        self._enabled = enabled
        self._capabilities = tuple(normalized_capabilities)
        self._context_window = context_window
        self._is_local = is_local
        self._requires_approval = requires_approval
        self._input_cost_per_1k_tokens = input_cost
        self._output_cost_per_1k_tokens = output_cost

    @staticmethod
    def _validate_identifier(value: str, field_name: str) -> str:
        """Validate and normalize a non-empty string identifier."""
        if not isinstance(value, str):
            raise TypeError(f"{field_name} must be a string.")

        normalized_value = value.strip()
        if not normalized_value:
            raise ValueError(f"{field_name} must not be empty.")

        return normalized_value

    @staticmethod
    def _validate_cost(
        value: float | None,
        field_name: str,
    ) -> float | None:
        """Validate an optional non-negative model cost."""
        if value is None:
            return None

        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{field_name} must be a number.")

        if not isfinite(value):
            raise ValueError(f"{field_name} must be a finite number.")

        if value < 0:
            raise ValueError(f"{field_name} must not be negative.")

        return float(value)

    @property
    def model_id(self) -> str:
        """Return the stable model identifier."""
        return self._model_id

    @property
    def provider_id(self) -> str:
        """Return the provider identifier."""
        return self._provider_id

    @property
    def model_name(self) -> str:
        """Return the provider-specific model name."""
        return self._model_name

    @property
    def enabled(self) -> bool:
        """Return whether the model is enabled."""
        return self._enabled

    @property
    def capabilities(self) -> tuple[str, ...]:
        """Return the model capabilities as an immutable tuple."""
        return self._capabilities

    @property
    def context_window(self) -> int | None:
        """Return the context window size when known."""
        return self._context_window

    @property
    def is_local(self) -> bool:
        """Return whether the model runs locally."""
        return self._is_local

    @property
    def requires_approval(self) -> bool:
        """Return whether model usage requires user approval."""
        return self._requires_approval

    @property
    def input_cost_per_1k_tokens(self) -> float | None:
        """Return the input cost per 1,000 tokens when known."""
        return self._input_cost_per_1k_tokens

    @property
    def output_cost_per_1k_tokens(self) -> float | None:
        """Return the output cost per 1,000 tokens when known."""
        return self._output_cost_per_1k_tokens
