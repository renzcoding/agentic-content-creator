# M11 — Legacy Conversation Migration

## Objective

Maintain backward compatibility with conversation history files created before session management was introduced in M10.

## Problem

Older versions stored conversation history as a JSON list:

    [
      {"role": "user", "content": "Old question"},
      {"role": "assistant", "content": "Old answer"}
    ]

M10 introduced a session-based JSON dictionary structure:

    {
      "default": [
        {"role": "user", "content": "Old question"},
        {"role": "assistant", "content": "Old answer"}
      ]
    }

Without migration, older files would no longer match the new storage structure.

## Implementation

`ConversationMemory._load()` now detects legacy list-based data.

When a list is detected, it:

1. Creates a session dictionary using the `default` session.
2. Preserves the existing messages and their order.
3. Writes the migrated structure to the original JSON file.
4. Returns the migrated session dictionary.

Migration occurs automatically when an operation loads the conversation data, including `get_history()`, `add_message()`, and `clear()`.

Existing dictionary-based session data remains unchanged.

## Error Handling

- Missing files return an empty dictionary.
- Invalid JSON and file read errors return an empty dictionary.
- Unsupported root data types return an empty dictionary.

## Tests

The conversation memory tests verify:

- Legacy list migration into the default session.
- Preservation of legacy messages when adding a new message.
- Existing session management and validation behavior.

Full test suite: **75 tests passed**.

## Limitations

- Migration modifies the original file in place.
- No automatic backup is created.
- JSON file storage is intended for local use and does not provide concurrent-write protection.
