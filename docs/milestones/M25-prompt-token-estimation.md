# M25 — Prompt Token Estimation

## Objective

Estimate the approximate token count of an LLM prompt before sending it to the configured provider.

## Configuration

Added the following settings in `config/settings.py`:

- `PROMPT_TOKEN_BUDGET = 2048`: Reserved maximum prompt token budget for a future enforcement stage.
- `CHARS_PER_TOKEN_ESTIMATE = 4`: Approximate character-to-token conversion ratio.

## Implementation

### 1. Token Estimator

File: `app/utils/token_estimator.py`

Added:

`estimate_tokens(text: str) -> int`

Behavior:

- Rejects non-string input with `TypeError`.
- Returns `0` for empty input.
- Estimates token count using configurable character ratio.
- Uses ceiling division to avoid rounding down partial token estimates.

This is a heuristic, not an exact tokenizer. Actual token counts depend on the model, tokenizer, language, and text content.

### 2. Product Manager Integration

File: `app/agents/product_manager.py`

Added `last_prompt_token_estimate` to store the latest prompt token estimate.

The estimate is calculated immediately before calling `self.provider.generate(prompt)`.

This milestone measures prompt size only. It does not enforce `PROMPT_TOKEN_BUDGET`, reject oversized prompts, or truncate content based on token count.

## Tests

Added `tests/test_token_estimator.py` to verify:

- Empty input returns zero.
- Exact character ratios are estimated correctly.
- Partial ratios round up.
- Non-string input raises `TypeError`.

Added a ProductManager integration test to verify that the estimate matches the prompt sent to the provider.

Test results:

- Focused tests: 22 passed.
- Full test suite: 127 passed.

## Limitations

- Token estimation uses a character ratio rather than the model's actual tokenizer.
- `PROMPT_TOKEN_BUDGET` is reserved for a future implementation and is not enforced in this milestone.
- The estimate may differ from the actual token count reported by the LLM provider.

## Result

Prompt token estimation is now available before provider generation, providing a baseline for future prompt budget management.
