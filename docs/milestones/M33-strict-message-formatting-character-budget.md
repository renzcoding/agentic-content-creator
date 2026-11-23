# M33 - Strict Character Budget for Formatted Conversation Messages

## Objective

Ensure formatted conversation messages never exceed the configured character budget, including newline separators.

## Problem

The previous implementation reduced the remaining character budget based on message line lengths but did not account for newline characters inserted by `"\n".join(lines)`.

As a result, the final formatted output could exceed the configured maximum character limit.

## Implementation

Updated `ProductManagerAgent._format_messages()` in `app/agents/product_manager.py`.

Changes:
- Return an empty string when the character budget is zero or negative.
- Reserve one character for each newline separator between messages.
- Calculate the available character budget before appending each message.
- Truncate the current message when it exceeds the available budget.
- Stop processing additional messages after truncation.

## Tests

Added three tests in `tests/test_product_manager.py`:

1. `test_format_messages_counts_newline_characters`
   - Verifies newline separators are included in the character budget.
2. `test_format_messages_never_exceeds_character_budget`
   - Verifies formatted output never exceeds the configured limit.
3. `test_format_messages_returns_empty_for_zero_budget`
   - Verifies a zero character budget returns an empty string.

## Validation

- Python compilation: passed.
- Focused ProductManagerAgent tests: 33 passed.
- Full test suite: 147 passed.

## Result

Conversation formatting now strictly respects its configured character budget, including newline separators.
