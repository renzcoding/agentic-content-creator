# M19 — Relevant Conversation Context Retrieval

## Objective

Integrate keyword-based conversation search into ProductManagerAgent so older relevant messages can be included in LLM prompts.

## Implementation

File: `app/agents/product_manager.py`

Updated `ProductManagerAgent.run()` to:

1. Retrieve all messages from the current session.
2. Keep the newest messages according to `history_limit`.
3. Extract keywords from the current task.
4. Search conversation messages using those keywords.
5. Exclude messages already included in recent history.
6. Preserve the original chronological order.
7. Add relevant older messages to the LLM prompt under `Relevant Previous Conversation`.

## Keyword Selection

- Uses words from the current task.
- Removes common surrounding punctuation.
- Converts keywords to lowercase using `casefold()`.
- Ignores words shorter than three characters.
- Uses the existing `ConversationMemory.search_messages()` method.

## Tests

File: `tests/test_product_manager.py`

Added a test verifying that an older message matching a task keyword is included in the prompt even when it falls outside the recent history limit.

Focused tests:

```bash
python -m unittest tests.test_product_manager -v
Result: 11 tests passed.

Full test suite:
python -m unittest discover -s tests -v


Result: 114 tests passed.

Code quality check:
git diff --check


Result: No whitespace errors.
Design Decisions
- Recent history and relevant older messages are presented in separate prompt sections.
- Search remains session-specific.
- Duplicate messages are excluded from the relevant section.
- Original conversation order is preserved.
- Existing storage backends remain unchanged.
Limitations
- Retrieval uses simple case-insensitive substring matching.
- Short keywords under three characters are ignored.
- Search relevance is not ranked or scored.
- Semantic search and embeddings are not implemented.
- Keyword searches currently scan conversation messages in application memory.
Milestone Checklist
- [x] Retrieve all messages from the active session.
- [x] Preserve the configured recent history limit.
- [x] Extract keywords from the current task.
- [x] Retrieve older matching messages.
- [x] Exclude duplicate recent messages.
- [x] Preserve chronological order.
- [x] Add relevant context to the LLM prompt.
- [x] Add regression test.
- [x] Run focused tests.
- [x] Run the full test suite.
- [x] Run git diff --check.
