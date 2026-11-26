# M41 — Orchestrator Evolution

## 1. Overview

M41 evolves AgentOrchestrator to use AgentRegistry as the single owner
of Agent registration and lookup.

The implementation preserves existing name-based APIs while delegating
Agent storage and identity lookup to the registry.

## 2. Architecture

AgentOrchestrator coordinates Agent registration and task execution.

AgentRegistry owns:
- Agent registration by permanent agent_id.
- Agent lookup by permanent ID.
- Agent lookup by name.
- Duplicate identity protection.
- Agent listing.

The Orchestrator does not maintain a separate registration store.

## 3. Implementation

### `app/agents/orchestrator.py`

#### `__init__(registry=None)`

Accepts an optional AgentRegistry dependency.

When no registry is supplied, the Orchestrator creates a new
AgentRegistry instance.

#### `agents` property

Provides a compatibility view of registered Agents using normalized
Agent names as dictionary keys.

The view is generated from the registry and is not a second data store.

#### `register_agent(agent)`

Validates the Agent type, checks for an existing name, and delegates
registration to AgentRegistry.

Duplicate names remain rejected to preserve previous behavior.

#### `list_agents()`

Returns the legacy list of dictionaries containing Agent names and
roles. The data is retrieved from AgentRegistry.

#### `execute(agent_name, task)`

Validates the requested name, resolves the Agent through
AgentRegistry, and calls the Agent's `run()` method.

Unknown and ambiguous names are rejected.

### `tests/test_orchestrator_registry_integration.py`

Adds six integration tests covering:
- Registry dependency injection.
- Registration by permanent Agent ID.
- Legacy name-keyed Agent access.
- Duplicate name rejection.
- Task execution through the registry.
- Legacy Agent listing format.

## 4. Compatibility

The following existing interfaces remain supported:
- `AgentOrchestrator()`
- `register_agent(agent)`
- `list_agents()`
- `execute(agent_name, task)`
- `agents` name-keyed lookup

The existing Orchestrator unit tests continue to pass.

## 5. Test Results

M41 integration tests: 6 passed.

Orchestrator and integration tests: 14 passed.

Full regression suite: 202 tests passed.

## 6. Scope Boundaries

M41 does not introduce:
- Multi-Agent task planning.
- AgentMessageBus.
- Workflow orchestration.
- Division execution.
- Persistent AgentRegistry storage.
- Workspace-scoped Agent registries.

These remain separate roadmap milestones.

## 7. Next Milestone

M42 — AgentMessageBus Foundation.

M42 will introduce the foundation for structured communication
between Agents without changing the M41 registration ownership model.

## 8. Definition of Done

- [x] Orchestrator accepts an injected AgentRegistry.
- [x] Agent registration delegates to AgentRegistry.
- [x] Agent lookup delegates to AgentRegistry.
- [x] Task execution resolves Agents through the registry.
- [x] Legacy name-based APIs remain compatible.
- [x] Integration tests added.
- [x] Full regression suite passed.
- [x] M41 documented.
