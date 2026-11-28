from math import isfinite

from app.services.llm.model_configuration import ModelConfiguration
from app.services.llm.model_usage_tracker import ModelUsageTracker
from app.utils.token_estimator import estimate_tokens


class BudgetExceededError(RuntimeError):
    """Raise when a model request exceeds its configured budget."""


class ModelBudgetManager:
    """Estimate and enforce per-model request budgets."""

    def __init__(
        self,
        usage_tracker: ModelUsageTracker,
        budget_limits: dict[str, float],
    ) -> None:
        """Initialize the manager with usage tracking and model budgets."""
        if not isinstance(usage_tracker, ModelUsageTracker):
            raise TypeError(
                "Usage tracker must be a ModelUsageTracker instance."
            )

        if not isinstance(budget_limits, dict):
            raise TypeError("Budget limits must be a dictionary.")

        normalized_limits = {}

        for model_id, limit in budget_limits.items():
            if not isinstance(model_id, str):
                raise TypeError("Budget model IDs must be strings.")

            normalized_model_id = model_id.strip()
            if not normalized_model_id:
                raise ValueError("Budget model IDs must not be empty.")

            if isinstance(limit, bool) or not isinstance(
                limit, (int, float)
            ):
                raise TypeError("Budget limits must be numeric.")

            if not isfinite(limit):
                raise ValueError("Budget limits must be finite.")

            if limit < 0:
                raise ValueError("Budget limits must not be negative.")

            if normalized_model_id in normalized_limits:
                raise ValueError(
                    f"Budget for '{normalized_model_id}' is duplicated."
                )

            normalized_limits[normalized_model_id] = float(limit)

        self._usage_tracker = usage_tracker
        self._budget_limits = normalized_limits

    @property
    def usage_tracker(self) -> ModelUsageTracker:
        """Return the usage tracker used for historical budget calculations."""
        return self._usage_tracker

    @staticmethod
    def _estimate_request_cost(
        configuration: ModelConfiguration,
        prompt: str,
        max_output_tokens: int,
    ) -> float:
        """Estimate request cost from input and reserved output tokens."""
        input_cost = configuration.input_cost_per_1k_tokens
        output_cost = configuration.output_cost_per_1k_tokens

        if input_cost is None or output_cost is None:
            raise ValueError(
                "Model pricing must be configured for budget enforcement."
            )

        input_tokens = estimate_tokens(prompt)

        return (
            input_tokens * input_cost
            + max_output_tokens * output_cost
        ) / 1000

    def check_request(
        self,
        configuration: ModelConfiguration,
        prompt: str,
        max_output_tokens: int,
    ) -> float | None:
        """Check budget before generation and return estimated request cost."""
        if not isinstance(configuration, ModelConfiguration):
            raise TypeError(
                "Configuration must be a ModelConfiguration instance."
            )

        if not isinstance(prompt, str):
            raise TypeError("Prompt must be a string.")

        if not prompt.strip():
            raise ValueError("Prompt must not be empty.")

        if isinstance(max_output_tokens, bool) or not isinstance(
            max_output_tokens, int
        ):
            raise TypeError("Maximum output tokens must be an integer.")

        if max_output_tokens <= 0:
            raise ValueError(
                "Maximum output tokens must be greater than zero."
            )

        model_id = configuration.model_id
        budget_limit = self._budget_limits.get(model_id)

        # Models without an explicit budget are not budget-restricted here.
        if budget_limit is None:
            return None

        estimated_request_cost = self._estimate_request_cost(
            configuration,
            prompt,
            max_output_tokens,
        )

        usage = self._usage_tracker.get_usage(model_id)
        current_cost = usage["estimated_cost"]

        if current_cost is None:
            raise BudgetExceededError(
                f"Cannot enforce budget for '{model_id}' because "
                "historical cost is unknown."
            )

        estimated_total_cost = current_cost + estimated_request_cost

        if estimated_total_cost > budget_limit:
            raise BudgetExceededError(
                f"Request exceeds budget for '{model_id}': "
                f"estimated total {estimated_total_cost:.6f}, "
                f"budget {budget_limit:.6f}."
            )

        return estimated_request_cost
