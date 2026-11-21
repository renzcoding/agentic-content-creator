# M20 — Conversation Relevance Ranking

## Objective

Improve conversation retrieval by ranking messages according to the number of matching search keywords.

## Implementation

File: `app/memory/conversation_memory.py`

Updated `ConversationMemory.search_messages()` to support:

- A single keyword or a list of keywords.
- Case-insensitive keyword matching.
- Relevance scoring based on unique matching keywords.
- Highest relevance score first.
- Original conversation order when scores are equal.
- Optional result limits applied after ranking.
- Session-specific retrieval.

## Relevance Scoring

Each message receives one point for every unique keyword found in its content.

Messages matching more keywords receive higher scores. Messages with equal scores retain their original conversation order.

## Tests

File: `tests/test_conversation_memory.py`

Added and updated tests for:

- Ranking messages by keyword matches.
- Preserving conversation order for equal scores.
- Applying result limits after ranking.

Focused tests: 23 passed.

Full test suite: 116 passed.

Code quality check: `git diff --check` passed.

## Design Decisions

- Uses simple keyword-based relevance scoring without external dependencies.
- Counts each unique keyword at most once per message.
- Uses case-insensitive substring matching.
- Preserves insertion order when relevance scores are equal.
- Applies the result limit after ranking.

## Limitations

- Matching is based on substrings, not semantic meaning.
- No TF-IDF, embeddings, or vector database is used.
- Every keyword has equal weight.
- A keyword appearing as part of another word can also match.
- Relevance scores are internal and are not returned in the public result.

## Milestone Checklist

- [x] Support multiple search keywords.
- [x] Calculate message relevance scores.
- [x] Sort messages by relevance.
- [x] Preserve original order for equal scores.
- [x] Apply result limits after ranking.
- [x] Preserve session isolation.
- [x] Add ranking tests.
- [x] Run focused tests.
- [x] Run the full test suite.
- [x] Run `git diff --check`.
