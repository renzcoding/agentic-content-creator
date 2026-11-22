# M21 — Optimized Relevant Conversation Retrieval

## Objective

Optimize relevant conversation retrieval by reducing repeated search calls in ProductManagerAgent.

## Implementation

File: `app/agents/product_manager.py`

Updated `ProductManagerAgent.run()` to:

- Extract keywords from the current task.
- Remove punctuation and normalize keywords to lowercase.
- Ignore keywords shorter than three characters.
- Pass all extracted keywords as a sorted list to `ConversationMemory.search_messages()`.
- Execute the conversation search once instead of once per keyword.
- Exclude messages already included in recent conversation history.
- Preserve the original conversation order when building the prompt.

## Performance Improvement

Previously, ProductManagerAgent called `search_messages()` separately for every keyword.

Now, it calls the method once with the complete keyword list.

This reduces repeated conversation storage reads and search operations.

## Tests

File: `tests/test_product_manager.py`

Added `test_searches_relevant_messages_with_multiple_keywords` to verify:

- Multiple task keywords are passed as a list.
- Only one search call is performed.
- The expected keywords are included.

Focused ProductManager tests: 12 passed.

Full test suite: 117 passed.

Code quality check: `git diff --check` passed.

## Design Decisions

- Reuses the existing multi-keyword search introduced in M20.
- Keeps keyword extraction inside ProductManagerAgent.
- Does not introduce external search dependencies.
- Retains compatibility with the existing conversation storage backends.

## Limitations

- Matching is based on case-insensitive substring matching, not semantic similarity.
- All matching messages are currently eligible for inclusion; no relevance threshold or result limit is applied here.
- Generic task words may produce less relevant matches.
- Original conversation order is preserved when constructing the prompt, so relevance ranking is not used to prioritize prompt sections.

## Milestone Checklist

- [x] Extract task keywords.
- [x] Normalize and filter keywords.
- [x] Search with multiple keywords in one call.
- [x] Avoid repeated search calls.
- [x] Exclude recent messages from older relevant context.
- [x] Add regression test for single-call behavior.
- [x] Run focused ProductManager tests.
- [x] Run the full test suite.
- [x] Run `git diff --check`.
