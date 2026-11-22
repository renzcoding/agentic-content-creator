# M23 — Relevant Context Limit

## Objective

Limit the number of older relevant conversation messages included in ProductManagerAgent prompts to control context growth.

## Implementation

### Configuration

File: `config/settings.py`

Added:

- `RELEVANT_CONTEXT_LIMIT = 5`

This setting controls the maximum number of relevance-ranked older messages included in an LLM prompt.

### Agent Integration

File: `app/agents/product_manager.py`

Updated ProductManagerAgent to:

1. Import `RELEVANT_CONTEXT_LIMIT`.
2. Retrieve older messages using task keywords.
3. Preserve the relevance ranking returned by ConversationMemory.
4. Exclude messages already included in recent conversation history.
5. Limit relevant messages to the configured maximum.

The five highest-ranked messages are retained by default.

## Testing

File: `tests/test_product_manager.py`

Added:

- `test_limits_relevant_context_messages`

The test verifies that:

- No more than five relevant older messages enter the prompt.
- Higher-ranked messages are retained.
- Lower-ranked messages are excluded.
- Relevance ordering is preserved.

## Validation Results

- Python compilation: passed.
- Focused ProductManagerAgent tests: 14 passed.
- Full test suite: 119 passed.
- No external dependencies added.

## Design Decisions

- Keep the limit configurable through application settings.
- Default the limit to five messages.
- Apply the limit after relevance ranking and recent-message exclusion.
- Preserve the existing recent conversation history behavior.

## Limitations

- The limit is based on message count, not token count.
- Long individual messages can still consume substantial context.
- The limit currently applies to ProductManagerAgent.

## Completion Checklist

- [x] Add relevant context limit configuration.
- [x] Integrate the limit into ProductManagerAgent.
- [x] Preserve relevance ranking.
- [x] Add regression test.
- [x] Run focused tests.
- [x] Run full test suite.
