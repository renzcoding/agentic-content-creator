# M22 — Relevance-Based Context Prioritization

## Objective

Ensure ProductManagerAgent preserves relevance ranking when retrieving older conversation messages for the LLM prompt.

## Problem

M20 introduced relevance ranking in ConversationMemory.search_messages().

However, ProductManagerAgent previously converted search results into a set and reconstructed messages using the original conversation order. This discarded the relevance ranking.

## Implementation

File: `app/agents/product_manager.py`

Updated ProductManagerAgent.run() to:

1. Extract meaningful keywords from the current task.
2. Search older conversation messages using one keyword list.
3. Receive messages in relevance-ranked order.
4. Exclude messages already included in recent conversation history.
5. Preserve the ranking when constructing the relevant context section.

## Testing

File: `tests/test_product_manager.py`

Added regression test:

- `test_prioritizes_more_relevant_messages_in_prompt`

The test verifies that a message matching more task keywords appears before a message with fewer matches.

## Validation Results

- Python compilation: passed.
- ProductManagerAgent tests: 13 passed.
- Full test suite: 118 passed.
- No external dependencies added.

## Design Decisions

- Reuse the ranking provided by ConversationMemory.
- Do not reconstruct search results from the original conversation list.
- Keep recent conversation history separate from older relevant context.
- Exclude recent messages from relevant context to avoid duplication.

## Limitations

- Search still uses case-insensitive substring matching rather than semantic similarity.
- Equal relevance scores preserve the original conversation order.
- All matching older messages are included; there is no separate token-budget limit for relevant context.

## Completion Checklist

- [x] Preserve relevance ranking in ProductManagerAgent.
- [x] Exclude recent messages from relevant context.
- [x] Add regression test for ranking order.
- [x] Run focused tests.
- [x] Run full test suite.
