# M29 — Recent History Priority & Preservation

## Objective

Verify that prompt budget enforcement preserves the newest conversation history and does not mutate the original history collection.

## History Reduction Behavior

When the prompt exceeds its token budget:

1. Older conversation history is removed first.
2. Newer conversation history is preserved as long as the budget allows.
3. The original history collection remains unchanged.
4. Required system instructions and the current task remain preserved.

## Tests Added

### `test_preserves_newest_history_when_reducing_prompt`

Verifies that:
- Older conversation history is removed first.
- Newer conversation history remains in the fitted prompt.
- The final prompt stays within the configured token budget.

### `test_preserves_original_history_when_reducing_prompt`

Verifies that:
- Prompt reduction removes older history when necessary.
- Newer history remains available.
- The original history list is not modified.
- The final prompt respects the token budget.

## Implementation Notes

The tests validate the existing history reduction behavior in `ProductManagerAgent._fit_prompt_to_budget()`.

The method copies the history collection before removing older messages, protecting the original data.

No production implementation changes were required.

## Validation

Command:

`python -m unittest discover -s tests -q`

Result:
- 138 tests passed.
- No test failures.

## Outcome

Recent history priority and preservation are covered by automated regression tests.
