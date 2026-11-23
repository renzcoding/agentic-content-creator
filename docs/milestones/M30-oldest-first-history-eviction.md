# M30 - Oldest-First History Eviction

## Objective

Verify that prompt token budget enforcement removes conversation history
from the oldest message to the newest message.

## Implementation

This milestone adds a regression test to
`tests/test_product_manager.py`.

### Test: `test_removes_history_in_oldest_first_order`

The test creates three conversation messages:

1. Oldest: Python conversation.
2. Middle: Laravel conversation.
3. Newest: React conversation.

It calculates a token budget that can retain the middle and newest messages
but cannot retain all three messages.

The test then verifies that:

- The oldest message is removed.
- The middle message is retained.
- The newest message is retained.
- The resulting prompt stays within the configured token budget.

## Technical Decisions

- No production code changes are required.
- The test uses the existing `estimate_tokens()` utility.
- The test verifies eviction order through observable prompt content.
- Existing conversation history must remain available to the caller.

## Validation

Focused test:

`python -m unittest tests.test_product_manager.TestProductManagerAgent.test_removes_history_in_oldest_first_order -v`

Full test suite:

`python -m unittest discover -s tests -v`

Result: 139 tests passed.

Whitespace validation:

`git diff --check`

Result: No errors.

## Files Changed

- `tests/test_product_manager.py`
- `docs/milestones/M30-oldest-first-history-eviction.md`

## Outcome

M30 confirms that older conversation messages are discarded before newer
messages when the prompt exceeds its token budget.
