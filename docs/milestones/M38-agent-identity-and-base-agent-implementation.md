# M38 — Agent Identity & BaseAgent Implementation

## 1. Overview

Milestone M38 implements the first stage of the AI Super App Core Foundation by strengthening the `BaseAgent` identity system.

The implementation introduces permanent UUID v4 identity, validates essential identity fields, and supports optional organizational metadata while preserving backward compatibility with existing agents.

This milestone focuses on the Agent identity foundation. Agent registration, organizational hierarchy, and identity-based memory migration remain separate responsibilities for future milestones.

## 2. Objectives

- Introduce a permanent UUID v4 for every Agent.
- Support restoring an Agent using an existing UUID.
- Prevent invalid Agent names and roles.
- Make `agent_id` read-only.
- Introduce optional organizational metadata.
- Preserve the existing BaseAgent constructor interface.
- Preserve existing memory namespace behavior.
- Maintain compatibility with existing Orchestrator behavior.
- Verify implementation through automated unit tests.

## 3. Files Changed

| File | Responsibility |
|---|---|
| `app/agents/base_agent.py` | Implements permanent Agent identity and metadata. |
| `tests/test_base_agent.py` | Tests Agent identity, validation, metadata, and compatibility. |
| `tests/test_orchestrator.py` | Verifies invalid Agent identity is rejected before registration. |
| `docs/milestones/M38-agent-identity-and-base-agent-implementation.md` | Documents implementation and architectural decisions. |

## 4. BaseAgent Implementation

### 4.1 UUID v4 Identity

The implementation uses Python's `uuid` module:

- `uuid4()` generates a new unique Agent identifier.
- `UUID()` parses an existing identifier.
- UUID version validation ensures the identifier is UUID v4.
- An existing valid identifier is preserved during restoration.

Every Agent receives a permanent `agent_id`.

The identifier is generated only when the caller does not provide one.

An invalid identifier raises an exception instead of silently generating a replacement.

### 4.2 Constructor Parameters

The updated constructor supports:

| Parameter | Type | Description |
|---|---|---|
| `name` | `str` | Agent display or call name. |
| `role` | `str` | Agent's primary responsibility. |
| `memory` | `BaseMemory \| None` | Optional memory implementation. |
| `agent_id` | `str \| None` | Existing UUID v4 for identity restoration. |
| `formal_name` | `str \| None` | Agent's formal organizational name. |
| `division_id` | `str \| None` | Identifier of the assigned division. |
| `manager_agent_id` | `str \| None` | Identifier of the Agent's manager. |

The original first three constructor parameters remain unchanged to preserve compatibility with existing implementations.

### 4.3 Identity Validation

The constructor validates the essential identity fields:

- An empty Agent name is rejected.
- A whitespace-only Agent name is rejected.
- An empty Agent role is rejected.
- A whitespace-only Agent role is rejected.

Valid names and roles are normalized using `strip()`.

Invalid identity data raises `ValueError`.

### 4.4 Read-Only Agent ID

The identifier is stored internally in `_agent_id`.

The `agent_id` property exposes the identifier without providing a public setter.

This prevents accidental reassignment through the public interface.

### 4.5 Organizational Metadata

The implementation introduces three optional organizational attributes:

- `formal_name`
- `division_id`
- `manager_agent_id`

These fields default to `None`.

They provide the initial foundation for future organizational relationships without introducing registration or hierarchy-management responsibilities into `BaseAgent`.

## 5. Memory Compatibility

The existing memory namespace implementation remains unchanged:

`f"{self.name}:{key}"`

The `remember()` method continues to save information using the Agent name as its namespace.

The `recall()` method continues to retrieve information using the same namespace.

This is intentional.

Changing memory namespaces from Agent names to UUIDs without a verified migration mechanism could make previously stored information inaccessible.

Therefore, memory namespace migration is explicitly excluded from M38.

Future migration must preserve existing data, support backward compatibility, and prevent cross-Agent memory access.

## 6. Architecture Decisions

### 6.1 BaseAgent Responsibility

`BaseAgent` is responsible for:

- Essential Agent identity.
- Identity validation.
- Permanent Agent identifier.
- Optional organizational metadata.
- Existing memory access interface.
- Abstract task execution interface.

### 6.2 Responsibilities Outside BaseAgent

The following responsibilities remain outside `BaseAgent`:

- Agent registration and lookup.
- Division registration and lookup.
- Manager hierarchy validation.
- Agent orchestration.
- Workspace access control.
- Agent permissions.
- Skill and Tool registration.
- Persistent Agent configuration.

These responsibilities will be implemented in their respective core components.

### 6.3 Backward Compatibility

Existing Agent implementations continue using the original constructor arguments:

`name`, `role`, and `memory`.

The new identity and organizational metadata parameters are optional.

Existing Orchestrator behavior is preserved in this milestone.

## 7. Test-Driven Development

The implementation followed a test-first approach.

The tests cover:

1. Rejecting empty Agent names.
2. Rejecting whitespace-only Agent names.
3. Rejecting empty Agent roles.
4. Rejecting whitespace-only Agent roles.
5. Generating UUID v4 automatically.
6. Accepting valid UUID v4 identifiers.
7. Preserving restored UUID identifiers.
8. Rejecting malformed UUID identifiers.
9. Rejecting UUID versions other than v4.
10. Preventing public reassignment of `agent_id`.
11. Accepting optional organizational metadata.
12. Defaulting optional metadata to `None`.
13. Preserving the legacy constructor interface.
14. Preserving existing abstract Agent behavior.
15. Preserving existing memory behavior.

The Orchestrator tests also verify that an Agent with invalid identity cannot be registered.

## 8. Test Results

The following commands were used:

Run BaseAgent tests:

`python -m unittest tests.test_base_agent -v`

Run Orchestrator tests:

`python -m unittest tests.test_orchestrator -v`

Run the complete test suite:

`python -m unittest discover -s tests -v`

Final full-suite result:

- Total tests: 165
- Passed: 165
- Failed: 0

Result: `OK`

The implementation also passed:

`git diff --check`

## 9. Definition of Done

| Requirement | Status |
|---|---|
| Permanent UUID v4 identity | Completed |
| UUID restoration | Completed |
| UUID version validation | Completed |
| Read-only Agent ID | Completed |
| Agent name validation | Completed |
| Agent role validation | Completed |
| Optional organizational metadata | Completed |
| Backward compatibility | Completed |
| Existing memory behavior preserved | Completed |
| Orchestrator regression tests | Completed |
| Full test suite | Passed |
| Milestone documentation | Completed |

## 10. Future Development

The following capabilities are intentionally deferred:

- AgentRegistry as the single owner of Agent registration and lookup.
- UUID-based Agent lookup.
- DivisionRegistry.
- Manager-Agent relationship validation.
- Workspace-aware Agent ownership.
- Persistent Agent identity storage.
- Backward-compatible memory namespace migration.
- Agent permissions and access policies.

These capabilities will be introduced incrementally in subsequent milestones.

## 11. Milestone Summary

M38 establishes the permanent identity foundation for the AI Super App.

Every Agent can now have a stable UUID v4, validated identity fields, and optional organizational metadata.

The implementation preserves existing Agent behavior and avoids introducing unrelated architectural responsibilities prematurely.

The milestone is considered implementation-complete based on the recorded test results. Git commit and push are tracked separately.
