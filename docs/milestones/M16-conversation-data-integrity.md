# M16 — Conversation Storage Data Integrity

## 1. Objective

Introduce centralized conversation data validation to prevent invalid
conversation structures from being persisted by JSON and SQLite storage.

Both storage backends must follow the same validation contract while
preserving their existing reliability mechanisms.

## 2. Background

Before M16, ConversationMemory validated messages before storage.
However, JSON and SQLite storage could also be called directly.

This allowed invalid data to bypass ConversationMemory validation.

M16 introduces a shared validator at the storage layer.

## 3. New Files

### app/memory/conversation_data_validator.py

Introduces the ConversationDataValidator class.

Method:

- validate(sessions: dict) -> None

Validation rules:

1. Sessions must be a dictionary.
2. Every session ID must be a non-empty string.
3. Every session's messages must be a list.
4. Every message must be a dictionary.
5. Every message must contain a non-empty string role.
6. Every message must contain a non-empty string content.

Invalid data raises ValueError.
Valid data returns None.

## 4. Modified Files

### app/memory/json_conversation_storage.py

- Imports ConversationDataValidator.
- Calls validate() before writing conversation data.
- Preserves atomic temporary-file replacement.
- Invalid data is rejected before temporary file creation.

### app/memory/sqlite_conversation_storage.py

- Imports ConversationDataValidator.
- Calls validate() before opening the database transaction for saving.
- Preserves transaction rollback behavior.
- Invalid data is rejected before database modification.

## 5. Test Files

### tests/test_conversation_data_validator.py

Eight tests cover:

1. Accept valid sessions.
2. Reject non-dictionary sessions.
3. Reject empty session IDs.
4. Reject non-list messages.
5. Reject non-dictionary messages.
6. Reject empty roles.
7. Reject empty content.
8. Reject non-string message fields.

### tests/test_json_conversation_storage.py

Adds a regression test verifying invalid data is rejected before persistence.

### tests/test_sqlite_conversation_storage.py

Adds a regression test verifying invalid data is rejected before persistence.

The existing rollback test was updated because invalid content is now
rejected before reaching SQLite.

A SQLite trigger deliberately rejects a validly structured message.
This verifies that a real database-level failure still rolls back the
transaction and preserves previously committed data.

## 6. Implementation Flow

1. A caller invokes storage.save(sessions).
2. ConversationDataValidator.validate(sessions) checks the input.
3. Invalid input raises ValueError.
4. Valid input proceeds to the selected storage backend.
5. JSON writes to a temporary file and replaces the original file.
6. SQLite performs delete-and-insert operations inside a transaction.

## 7. Development Commands

Create the validator:

```bash
cat > app/memory/conversation_data_validator.py
Run validator tests:
python -m unittest tests.test_conversation_data_validator -v


Run JSON storage tests:
python -m unittest tests.test_json_conversation_storage -v


Run SQLite storage tests:
python -m unittest tests.test_sqlite_conversation_storage -v


Run both storage test suites:
python -m unittest tests.test_json_conversation_storage tests.test_sqlite_conversation_storage -v


Run the complete project test suite:
python -m unittest discover -s tests -v


Check patch formatting:
git diff --check


8. Test Results
Test group	Result
Conversation data validator	8 passed
JSON conversation storage	6 passed
SQLite conversation storage	5 passed
Combined storage tests	13 passed
Complete project suite	104 passed

Full test command:
python -m unittest discover -s tests -v


Observed result:
Ran 104 tests
OK


9. Debugging and Lessons Learned
SQLite rollback test expectation
The previous rollback test supplied content=None and expected sqlite3.Error.

After validation was introduced, the validator correctly rejected that
input with ValueError before SQLite received it.

The test was changed to create a SQLite trigger that deliberately raises
a database integrity error for a validly structured message.

This preserves two independent guarantees:
- Input validation rejects invalid conversation structures.
- SQLite transactions protect existing data when database operations fail.
10. Design Decisions
- Centralize validation instead of duplicating it across backends.
- Use the same validator for JSON and SQLite.
- Raise ValueError consistently for invalid input.
- Validate before persistence operations.
- Preserve JSON atomic replacement.
- Preserve SQLite transaction rollback.
- Keep existing storage APIs unchanged.
11. Limitations
- Validation runs during save(), not when loading existing data.
- Legacy list-based JSON loading remains supported by the existing
  ConversationMemory migration mechanism.
- The validator does not enforce a fixed set of role names.
- Additional message dictionary fields are not rejected.
- Empty session dictionaries and empty message lists are accepted.
- Existing persisted data is not automatically repaired or migrated.
12. Milestone Completion
- [x] Create centralized conversation data validator.
- [x] Add validator unit tests.
- [x] Integrate validator with JSON storage.
- [x] Integrate validator with SQLite storage.
- [x] Add JSON storage regression test.
- [x] Add SQLite storage regression test.
- [x] Preserve SQLite transaction rollback behavior.
- [x] Run complete project test suite.
- [x] Record implementation and test results.
Status: Implementation and tests completed.
