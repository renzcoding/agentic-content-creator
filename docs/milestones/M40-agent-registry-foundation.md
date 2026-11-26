# M40 — AgentRegistry Foundation

## 1. Overview

M40 introduces AgentRegistry as the central owner of Agent registration,
identity-based lookup, and registration lifecycle management.

The implementation follows the architecture contract established in M37
and preserves the existing AgentOrchestrator implementation for the
separate M41 migration.

## 2. Architectural Position

AgentRegistry is located in `app/core/agent_registry.py`.

Its responsibilities are:
- Register BaseAgent instances using permanent agent_id values.
- Retrieve Agents by permanent ID.
- Reject duplicate Agent IDs.
- Explicitly unregister Agents.
- List registered Agents in insertion order.
- Support case-insensitive secondary name lookup.
- Reject ambiguous name lookups.

AgentRegistry does not execute tasks, invoke LLM providers, manage
workflows, or own Division membership.

## 3. Files Created

### `app/core/agent_registry.py`

Implements the AgentRegistry class.

- `__init__()`: Initializes an empty in-memory Agent dictionary.
- `register(agent)`: Validates the BaseAgent type, rejects duplicate
  permanent IDs, and registers the Agent.
- `get(agent_id)`: Returns the matching Agent or None.
- `unregister(agent_id)`: Removes and returns the Agent, or None when
  the identifier is unknown.
- `list_agents()`: Returns a new list of registered Agents in insertion
  order.
- `get_by_name(name)`: Performs case-insensitive secondary lookup.
  Returns None when no match exists and raises ValueError when multiple
  Agents share the requested name.

### `tests/test_agent_registry.py`

Contains 11 unit tests covering registration, duplicate detection,
type validation, identity lookup, removal, listing, name lookup,
unknown names, and ambiguous names.

## 4. Identity and Registration Rules

The permanent UUID v4 `agent_id` is the primary registry key.

Agent names are not unique identifiers. Multiple Agents may share
the same display name, but a name lookup must reject ambiguous results
instead of selecting an arbitrary Agent.

Registration accepts only BaseAgent instances.

## 5. Error Handling

- Invalid registration type: TypeError.
- Duplicate Agent ID: ValueError.
- Empty name lookup: ValueError.
- Ambiguous name lookup: ValueError.
- Unknown ID lookup: None.
- Unknown ID removal: None.
- Unknown name lookup: None.

## 6. Test Results

M40-specific tests: 11 passed.

Full regression suite: 196 tests passed.

The existing AgentOrchestrator tests continue to pass. No Orchestrator
migration was performed in M40.

## 7. Design Decisions

- AgentRegistry is placed under `app/core` because it is a core
  infrastructure component.
- Permanent Agent IDs are the primary identity.
- Name lookup remains a compatibility mechanism only.
- Registration order is preserved.
- The registry returns a copy of its collection when listing Agents.
- DivisionRegistry remains independent.
- Orchestrator delegation is intentionally deferred to M41.

## 8. Scope Boundaries

M40 does not introduce:
- Orchestrator migration.
- Agent task execution.
- Multi-Agent coordination.
- Division assignment automation.
- Persistence or database integration.
- Workspace-scoped registries.

These capabilities remain separate architectural concerns.

## 9. Roadmap

M40 — AgentRegistry Foundation: completed.

M41 — Orchestrator Evolution:
- Inject or compose AgentRegistry.
- Delegate Agent registration and lookup.
- Preserve existing `register_agent()`, `list_agents()`,
  and `execute(agent_name, task)` behavior.
- Resolve Agents by permanent ID internally where appropriate.
- Preserve legacy name-based execution compatibility.
- Keep task execution separate from registry responsibilities.

## 10. Definition of Done

- [x] AgentRegistry implementation created.
- [x] Permanent ID registration and lookup implemented.
- [x] Duplicate ID protection implemented.
- [x] Explicit unregister operation implemented.
- [x] Agent listing implemented.
- [x] Secondary name lookup implemented.
- [x] Ambiguous name lookup rejected.
- [x] Unit tests created.
- [x] Full regression suite passed.
- [x] Existing Orchestrator behavior preserved.
