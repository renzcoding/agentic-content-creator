from app.services.llm.model_configuration import ModelConfiguration


class ModelUsageTracker:
    """Track request, token, and estimated cost usage by model."""

    def __init__(self) -> None:
        """Initialize empty usage statistics."""
        self._usage: dict[str, dict[str, int | float | None]] = {}
        self._pricing_complete: dict[str, bool] = {}

    @staticmethod
    def _validate_token_count(value: int, field_name: str) -> int:
        """Validate a non-negative integer token count."""
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"{field_name} must be an integer.")

        if value < 0:
            raise ValueError(f"{field_name} must not be negative.")

        return value

    def record_usage(
        self,
        configuration: ModelConfiguration,
        input_tokens: int,
        output_tokens: int,
    ) -> dict[str, int | float | None]:
        """Record one model request and return updated usage statistics."""
        if not isinstance(configuration, ModelConfiguration):
            raise TypeError(
                "Configuration must be a ModelConfiguration instance."
            )

        validated_input_tokens = self._validate_token_count(
            input_tokens,
            "Input tokens",
        )
        validated_output_tokens = self._validate_token_count(
            output_tokens,
            "Output tokens",
        )

        model_id = configuration.model_id

        if model_id not in self._usage:
            # Initialize usage counters for the first request.
            self._usage[model_id] = {
                "request_count": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost": 0.0,
            }
            self._pricing_complete[model_id] = True

        usage = self._usage[model_id]

        # Update request and token totals.
        usage["request_count"] += 1
        usage["input_tokens"] += validated_input_tokens
        usage["output_tokens"] += validated_output_tokens

        input_cost = configuration.input_cost_per_1k_tokens
        output_cost = configuration.output_cost_per_1k_tokens

        if input_cost is None or output_cost is None:
            # Mark cumulative cost as unknown if pricing is incomplete.
            self._pricing_complete[model_id] = False
            usage["estimated_cost"] = None
        elif self._pricing_complete[model_id]:
            # Estimate request cost using configured per-1K token rates.
            request_cost = (
                validated_input_tokens * input_cost
                + validated_output_tokens * output_cost
            ) / 1000

            usage["estimated_cost"] += request_cost

        return self.get_usage(model_id)

    def get_usage(
        self,
        model_id: str,
    ) -> dict[str, int | float | None]:
        """Return a copy of usage statistics for one model."""
        if not isinstance(model_id, str):
            raise TypeError("Model ID must be a string.")

        normalized_id = model_id.strip()
        if not normalized_id:
            raise ValueError("Model ID must not be empty.")

        usage = self._usage.get(normalized_id)

        if usage is None:
            return {
                "request_count": 0,
                "input_tokens": 0,
                "output_tokens": 0,
                "estimated_cost": 0.0,
            }

        return dict(usage)

    def list_usage(
        self,
    ) -> dict[str, dict[str, int | float | None]]:
        """Return copies of usage statistics for all tracked models."""
        return {
            model_id: dict(usage)
            for model_id, usage in self._usage.items()
        }
