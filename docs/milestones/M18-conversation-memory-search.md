# M18 — Conversation Memory Search

## Objective

Add keyword-based search to conversation memory without coupling the feature to a specific storage backend.

## Implementation

File: `app/memory/conversation_memory.py`

Added `search_messages()`:

```python
search_messages(
    keyword: str,
    session_id: str = "default",
    limit: int | None = None,
) -> list[dict[str, str]]
Parameters
- keyword: Text to search for in message content.
- session_id: Conversation session to search. Defaults to default.
- limit: Optional maximum number of matching messages to return.
Behavior
- Searches message content using substring matching.
- Uses casefold() for case-insensitive matching.
- Trims whitespace around the keyword.
- Rejects empty keywords and session identifiers.
- Rejects non-positive limits.
- Preserves chronological order among returned messages.
- When a limit is supplied, returns the newest matching messages.
- Returns an empty list when no messages match.
Tests
File: tests/test_conversation_memory.py

Added seven tests covering:
1. Keyword search.
2. Case-insensitive matching.
3. Session isolation.
4. Search result limits.
5. Empty keyword rejection.
6. Invalid search limit rejection.
7. Empty session identifier rejection.
Validation
Focused tests:
python -m unittest tests.test_conversation_memory -v


Result: 21 tests passed.

Full test suite:
python -m unittest discover -s tests -v


Result: 113 tests passed.

Code quality check:
git diff --check


Result: No whitespace errors.
Design Decisions
- Search is implemented in ConversationMemory, not in individual storage backends.
- Both JSON and SQLite remain compatible through the existing storage abstraction.
- Search is limited to message content; role metadata is not searched.
- Results retain their original chronological order.
Milestone Checklist
- [x] Implement keyword search.
- [x] Support case-insensitive matching.
- [x] Support session-specific search.
- [x] Support result limits.
- [x] Validate search parameters.
- [x] Add seven regression tests.
- [x] Run focused tests.
- [x] Run the full test suite.
- [x] Run git diff --check.
  EOF
