# M24 — Prompt Context Budget

## Objective

Control the amount of historical and persistent context included in ProductManagerAgent prompts using configurable character budgets.

## Configuration

File: `config/settings.py`

Added three settings:

| Setting | Default | Purpose |
|---|---:|---|
| `RELEVANT_CONTEXT_CHAR_LIMIT` | 2000 | Maximum characters for relevant older messages |
| `RECENT_HISTORY_CHAR_LIMIT` | 2000 | Maximum characters for recent conversation |
| `PROJECT_CONTEXT_CHAR_LIMIT` | 1000 | Maximum characters for persistent project context |

## Implementation

File: `app/agents/product_manager.py`

### `_limit_text(text, max_chars)`

A static helper that trims a string to the specified character limit.

### `_format_messages(messages, max_chars)`

A static helper that formats conversation messages using `role: content` and keeps the combined formatted output within the supplied character budget.

Messages retain their original order. If the remaining budget is insufficient for a message, its text is truncated.

### Prompt Integration

`ProductManagerAgent.run()` now:

1. Retrieves persistent project context and applies its character limit.
2. Retrieves recent conversation history and formats it within its character budget.
3. Retrieves relevance-ranked older messages, preserving the M23 message-count limit.
4. Formats relevant older messages within their character budget.
5. Builds the final prompt using the bounded context sections.

## Testing

File: `tests/test_product_manager.py`

Added three regression tests:

- `test_limits_recent_conversation_characters`
- `test_limits_relevant_context_characters`
- `test_limits_project_context_characters`

Updated the default memory mock response to `None`, matching the expected behavior when no project context exists.

## Validation Results

- Python compilation: passed.
- Focused ProductManagerAgent tests: 17 passed.
- Full test suite: 122 passed.
- `git diff --check`: clean.
- No external dependencies added.

## Design Decisions

- Use character budgets instead of token budgets to avoid adding tokenizer dependencies.
- Keep each budget configurable through application settings.
- Preserve existing message relevance ranking and ordering.
- Keep the M23 relevant-message count limit in place.

## Limitations

- Character count is an approximation, not an exact token count.
- The current implementation truncates text and may cut a sentence mid-way.
- Prompt instructions and the current task are outside these context budgets.
- The three budgets are independent, so total prompt size can still vary.

## Completion Checklist

- [x] Add configurable character budgets.
- [x] Add text and message formatting helpers.
- [x] Apply limits to project context.
- [x] Apply limits to recent conversation.
- [x] Apply limits to relevant older conversation.
- [x] Add regression tests.
- [x] Run focused tests.
- [x] Run full test suite.
