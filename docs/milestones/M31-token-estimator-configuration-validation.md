# M31 — Token Estimator Configuration Validation

## Objective

Ensure token estimation rejects invalid character-to-token configuration values.

## Implementation

File: `app/utils/token_estimator.py`

Updated `estimate_tokens(text: str) -> int` to validate
`CHARS_PER_TOKEN_ESTIMATE` before performing token calculations.

Behavior:

- Rejects non-string input with `TypeError`.
- Rejects zero or negative character ratios with `ValueError`.
- Returns zero for empty input.
- Estimates tokens using the configured character ratio.
- Rounds up partial token estimates.

## Tests

File: `tests/test_token_estimator.py`

Added tests:

- `test_rejects_zero_character_ratio`
- `test_rejects_negative_character_ratio`

Existing tests continue to verify empty input, exact character ratios,
partial-token rounding, and non-string input rejection.

## Validation

Focused tests:

`python -m unittest tests.test_token_estimator -v`

Result: 6 tests passed.

Full test suite:

`python -m unittest discover -s tests -v`

Result: 141 tests passed.

## Technical Decisions

- Configuration validation occurs before token calculation.
- Invalid configuration raises `ValueError`.
- The existing character-based estimation algorithm remains unchanged.
- Tests use `unittest.mock.patch` to simulate invalid configuration
  without modifying application settings.

## Files Changed

- `app/utils/token_estimator.py`
- `tests/test_token_estimator.py`
- `docs/milestones/M31-token-estimator-configuration-validation.md`

## Outcome

The token estimator now rejects zero and negative character ratios,
preventing invalid token calculations caused by configuration errors.
