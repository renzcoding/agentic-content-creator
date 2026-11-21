# M17 — Conversation Data Integrity on Load

## Objective

Validate persisted conversation data whenever a storage backend loads it.
Prevent structurally invalid conversation records from entering application memory.

## Implementation

### 1. JSON Conversation Storage

File: `app/memory/json_conversation_storage.py`

- Validate dictionary-based session data after JSON decoding.
- Validate legacy list-based conversation data using the default session structure.
- Raise `ValueError` for unsupported root data types.
- Preserve existing behavior for missing files and malformed JSON syntax.

### 2. SQLite Conversation Storage

File: `app/memory/sqlite_conversation_storage.py`

- Group database records by session.
- Validate the reconstructed session data before returning it.
- Reject invalid session identifiers, roles, and message content.

### 3. Regression Tests

Files:
- `tests/test_json_conversation_storage.py`
- `tests/test_sqlite_conversation_storage.py`

Added tests verify that both backends reject invalid persisted conversation data during loading.

Existing tests continue to cover legacy JSON loading and migration, persistence, message ordering, and SQLite rollback.

## Validation

Focused tests:

```bash
python -m unittest tests.test_json_conversation_storage tests.test_sqlite_conversation_storage -v
Result: 15 tests passed.

Full test suite:
python -m unittest discover -s tests -v


Result: 106 tests passed.

Code quality check:
git diff --check


Result: No whitespace errors.
Design Decisions
- Validate data at the storage boundary, before returning it to application code.
- Keep malformed JSON syntax handling unchanged.
- Preserve legacy list-based JSON compatibility.
- Use the existing ConversationDataValidator to maintain consistent validation rules across storage backends.
Milestone Checklist
- [x] Validate JSON data during loading.
- [x] Validate SQLite data during loading.
- [x] Preserve legacy JSON compatibility.
- [x] Add regression tests for invalid stored data.
- [x] Run focused tests.
- [x] Run the full test suite.
- [x] Run git diff --check.
  EOF
