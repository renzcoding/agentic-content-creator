# M15 — Conversation Storage Reliability & Error Handling

## Objective

Improve conversation storage reliability and verify data integrity during failed storage operations.

## Implementation

### JSON Storage

- Added atomic file replacement during save operations.
- Conversation data is written to a temporary file first.
- The temporary file replaces the original only after a successful write.
- Leftover temporary files are cleaned up after failed writes.

### SQLite Storage

- Verified transaction rollback behavior during failed inserts.
- Existing conversation data remains intact when a database constraint fails.
- No SQLite implementation changes were required because transaction handling already provides rollback.

## Tests

### JSON Storage

- Preserve existing data when temporary writes fail.
- Remove temporary files after failed writes.
- Replace existing data after successful writes.
- Preserve existing loading and legacy format behavior.

### SQLite Storage

- Roll back failed insert transactions.
- Preserve previously committed conversation data.
- Preserve message ordering and session isolation.

### Full Test Suite

- 94 tests passed.

## Design Decisions

- JSON uses temporary-file replacement to reduce the risk of corrupted storage files.
- SQLite relies on its existing transaction context manager for atomic database operations.
- Storage errors are allowed to propagate from save operations so callers can handle failures.

## Limitations

- JSON temporary-file naming is currently fixed and is not designed for concurrent writers.
- Atomic replacement does not guarantee durability against every hardware or filesystem failure.
- SQLite concurrency and busy-timeout policies remain future improvements.
