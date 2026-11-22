# M27 — Prompt Context Priority & Preservation

## Objective

Verify that prompt token budget enforcement preserves the most valuable context and does not mutate the original context collections.

## Context Reduction Priority

When the prompt exceeds its token budget, optional context is removed in this order:

1. Relevant messages, starting with the lowest-ranked message.
2. Recent conversation history, starting with the oldest message.
3. Project context.
4. If required instructions and the current task still exceed the budget, raise a `ValueError`.

## Preservation Guarantees

- The highest-ranked relevant messages are retained as long as the token budget allows.
- Original history and relevant message lists remain unchanged during prompt reduction.
- The final prompt must stay within the configured token budget.
- Required instructions and the current task are not removed.

## Tests Added

### `test_preserves_original_context_lists_when_reducing_prompt`

Verifies that:
- Large project context is removed when necessary.
- The resulting prompt fits the configured token budget.
- The original history list remains unchanged.
- The original relevant messages list remains unchanged.

### `test_preserves_highest_ranked_relevant_message`

Verifies that:
- The highest-priority relevant message remains in the fitted prompt.
- The lower-priority message is removed when the budget requires it.
- The required prompt content fits the configured budget.
- The final prompt respects the token budget.

## Validation

Command:

`python -m unittest discover -s tests -q`

Result:
- 133 tests passed.
- No test failures.

## Implementation Notes

This milestone adds regression tests for the context-preservation behavior in `ProductManagerAgent._fit_prompt_to_budget()`.

The implementation copies the history and relevant message collections before removing optional context. This prevents prompt fitting from modifying the caller's original lists.

## Outcome

Prompt context priority and preservation behavior are covered by automated tests.
