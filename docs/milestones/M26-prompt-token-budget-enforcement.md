# M26 — Prompt Token Budget Enforcement

## Objective

Enforce a configurable token budget when building prompts for the Product Manager Agent.

## Implementation

File: `app/agents/product_manager.py`

Implemented:

- Added configurable `prompt_token_budget` to ProductManagerAgent.
- Rejects non-positive token budgets.
- Estimates prompt size before sending it to the LLM provider.
- Removes optional context when the prompt exceeds its budget.
- Preserves the current objective and required system instructions.
- Raises ValueError when required prompt content alone exceeds the budget.
- Copies conversation lists before reducing context to avoid modifying original data.

## Context Reduction Priority

Optional context is removed in this order:

1. Relevant previous conversation, starting with the lowest-ranked messages.
2. Recent conversation history, starting with the oldest messages.
3. Persistent project context.

Required system instructions and the current objective are never intentionally removed.

## Token Estimation

The implementation uses the approximate character-to-token ratio configured through `CHARS_PER_TOKEN_ESTIMATE`.

This is a heuristic, not an exact tokenizer. Actual token usage may differ depending on the model.

## Configuration

`config/settings.py`:

- `PROMPT_TOKEN_BUDGET = 2048`
- `CHARS_PER_TOKEN_ESTIMATE = 4`

## Validation

Added tests covering:

- Custom token budget configuration.
- Invalid token budget rejection.
- Prompt reduction within the configured budget.
- Required prompt overflow rejection.
- Provider not being called when required content exceeds the budget.

Full test suite: 131 tests passed.

## Result

The Product Manager Agent now limits estimated prompt size while prioritizing required instructions and the current task over optional memory context.
