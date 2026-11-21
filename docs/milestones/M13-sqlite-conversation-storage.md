# M13 — SQLite Conversation Storage

## Objective

Add SQLite as an alternative persistent storage backend for conversation memory without changing the existing ConversationMemory or ProductManagerAgent interfaces.

## Implementation

- Added `SQLiteConversationStorage` implementing `BaseConversationStorage`.
- Uses Python's built-in `sqlite3` module without external dependencies.
- Creates the `conversation_messages` table automatically.
- Stores session ID, message role, and message content.
- Preserves message order using an auto-incrementing ID.
- Uses parameterized SQL statements.
- Supports multiple independent conversation sessions.
- Uses `contextlib.closing` to ensure database connections are closed.
- Supports dependency injection through `ConversationMemory(storage=...)`.

## Tests

- Added four SQLite storage unit tests.
- Added one ConversationMemory integration test.
- Full test suite: 85 tests passed.
- Verified SQLite tests with ResourceWarning treated as an error.
- `git diff --check` completed successfully.

## Design Decisions

- JSON remains the default storage backend.
- SQLite is selected explicitly through dependency injection.
- Existing ConversationMemory and ProductManagerAgent behavior remains compatible.
- SQLite uses the Python standard library.

## Current Limitations

- No automatic migration utility from existing JSON files to SQLite.
- Saving currently replaces all stored conversation records.
- Concurrent writes from multiple ConversationMemory instances are not optimized.
- Database configuration and advanced SQLite tuning are not exposed yet.

## Result

Conversation storage now supports interchangeable JSON and SQLite backends through a shared abstraction.
