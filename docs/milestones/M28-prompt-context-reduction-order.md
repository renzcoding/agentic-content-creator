# M28 — Prompt Context Reduction Order

## Objective

Verify that optional prompt context is removed in the correct priority order when the configured token budget is exceeded.

## Context Reduction Priority

The prompt reduction process follows this order:

1. Relevant messages: remove the lowest-ranked message first.
2. Recent conversation history: remove the oldest message first.
3. Project context: remove persistent project context.
4. Required system instructions and the current task remain preserved.

If required content alone exceeds the token budget, the agent raises a ValueError.

## Tests Added

### `test_reduces_relevant_messages_before_history_and_project_context`

Verifies that relevant messages are removed while recent history and project context remain.

### `test_reduces_history_before_project_context`

Verifies that conversation history is removed while project context remains.

### `test_removes_project_context_after_history`

Verifies that project context is removed only after conversation history has been exhausted, while the current task remains present.

## Validation

Command:

`python -m unittest discover -s tests -q`

Result:
- 136 tests passed.
- No test failures.

## Implementation Notes

The tests validate the existing reduction order in `ProductManagerAgent._fit_prompt_to_budget()`.

No production implementation changes were required.

## Outcome

The prompt context reduction priority is covered by automated regression tests.
