# M14 — Conversation Storage Configuration

## Objective

Centralize conversation storage backend selection through application settings.

## Implementation

- Added conversation storage configuration to `config/settings.py`.
- Added `create_conversation_storage()` factory.
- Supported JSON and SQLite storage backends.
- Updated `ConversationMemory` to use the factory by default.
- Preserved custom `file_path` compatibility.
- Preserved dependency injection through `BaseConversationStorage`.

## Configuration

- `CONVERSATION_STORAGE_BACKEND`: Selects `json` or `sqlite`.
- `CONVERSATION_JSON_PATH`: Configures the JSON storage path.
- `CONVERSATION_SQLITE_PATH`: Configures the SQLite database path.

## Tests

- JSON backend creation.
- SQLite backend creation.
- Unsupported backend rejection.
- Custom JSON path compatibility.
- Default JSON path from application settings.
- Full test suite: 91 tests passed.

## Design Decisions

- Storage selection is centralized in a factory.
- Conversation management remains independent of storage implementation.
- Existing custom storage injection remains supported.
- JSON remains the default backend.

## Limitations

- Backend selection currently uses static application settings.
- No automatic migration between JSON and SQLite.
- SQLite concurrency and performance tuning remain future work.
