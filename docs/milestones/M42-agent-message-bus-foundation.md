# M42 — AgentMessageBus Foundation

## 1. Overview

M42 introduces the foundation for structured communication between
Agents through validated messages and an in-memory message bus.

The implementation is synchronous and does not trigger Agent execution.

## 2. Architecture

Two components are introduced:

- AgentMessage: represents a structured message exchanged between Agents.
- AgentMessageBus: stores messages and provides receiver-based retrieval.

Messages use permanent UUID v4 identifiers for the message, sender,
and receiver.

## 3. Implementation

### `app/core/agent_message.py`

#### `AgentMessage`

Represents a validated Agent communication message.

Constructor parameters:

- `sender_agent_id`: permanent UUID v4 of the sending Agent.
- `receiver_agent_id`: permanent UUID v4 of the receiving Agent.
- `message_type`: non-empty message classification.
- `payload`: dictionary containing message data.
- `message_id`: optional existing UUID v4 for restoration.
- `timestamp`: optional datetime; defaults to the current UTC time.

Properties expose message identity, sender, receiver, type, payload,
and timestamp.

The payload property returns a shallow copy to protect the stored
top-level dictionary from direct modification.

### `app/core/agent_message_bus.py`

#### `AgentMessageBus.__init__()`

Initializes an in-memory dictionary keyed by message ID.

#### `_normalize_uuid(value, field_name)`

Validates UUID v4 identifiers and returns their normalized string form.

#### `send(message)`

Accepts AgentMessage instances, rejects invalid types and duplicate
message IDs, and stores messages in insertion order.

#### `receive(agent_id)`

Returns messages addressed to the specified Agent in insertion order.
Receiving messages does not remove them from message history.

#### `get_message(message_id)`

Retrieves a message by its normalized permanent message ID.
Returns None when the message does not exist.

#### `list_messages()`

Returns all stored messages in insertion order as a new list.

## 4. Tests

### `tests/test_agent_message.py`

Covers generated and restored IDs, attribute preservation, UUID
validation, message type validation, and read-only message identity.

### `tests/test_agent_message_bus.py`

Covers message sending, invalid types, duplicate IDs, receiver-based
delivery, UUID normalization, invalid identifiers, message lookup,
history preservation, and insertion order.

## 5. Scope Boundaries

M42 provides an in-memory synchronous communication foundation only.

It does not introduce:

- Automatic Agent execution.
- Asynchronous message processing.
- Persistent message storage.
- Retry or delivery guarantees.
- EventManager integration.
- Workflow orchestration.
- Workspace-scoped message routing.

These capabilities remain future extensions.

## 6. Test Results

AgentMessage and AgentMessageBus tests: 21 passed.

Full regression suite: 223 tests passed.

## 7. Next Milestone

M43 — Integration and Regression Testing.

M43 will verify compatibility between the core foundation components
without introducing unnecessary changes to their ownership boundaries.

## 8. Definition of Done

- [x] Structured AgentMessage implementation.
- [x] UUID v4 identity validation.
- [x] In-memory AgentMessageBus implementation.
- [x] Receiver-based message retrieval.
- [x] Message history preservation.
- [x] Duplicate message rejection.
- [x] UUID normalization and lookup validation.
- [x] Unit tests added.
- [x] Full regression suite passed.
- [x] M42 reviewed and committed.
