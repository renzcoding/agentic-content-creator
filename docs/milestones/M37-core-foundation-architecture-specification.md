# M37 - Core Foundation Architecture Specification

## 1. Objective

Define the architecture and implementation contracts for the AI Super App core foundation.

The design must support a modular, extensible, local-first AI organization while preserving the existing Agentic Content Creator application and its tested behavior.

M37 is a design and documentation milestone. Application implementation is not part of this milestone.

## 2. Architecture Principles

- Modular Monolith: components have explicit responsibilities and boundaries.
- Backward Compatibility: existing agents and workflows remain operational during migration.
- Stable Identity: agents use permanent identifiers independent of mutable names and roles.
- Dependency Injection: providers, memory, and other dependencies remain injectable.
- Separation of Concerns: identity, registry, division management, orchestration, and communication are separate responsibilities.
- Incremental Migration: replace or extend existing components gradually.
- Testability: every implementation stage must have unit and integration tests.

## 3. Agent Identity Contract

### 3.1 Permanent Identifier

Every Agent must have an `agent_id`.

- Format: UUID version 4.
- Representation: string.
- New agents receive a generated UUID when no identifier is supplied.
- Existing persisted agents must reuse their stored identifier when loaded.
- The identifier is immutable during the Agent lifecycle.
- Names and roles must never be used as permanent identity keys.

### 3.2 Identity Metadata

The planned Agent identity fields are:

| Field | Purpose | Mutability |
|---|---|---|
| agent_id | Permanent Agent identity | Immutable |
| name | Display and calling name | Mutable |
| formal_name | Formal organizational title | Mutable |
| role | Functional responsibility | Mutable |
| division_id | Owning division reference | Mutable through controlled reassignment |
| manager_agent_id | Direct manager reference | Mutable through controlled reassignment |

Additional capabilities such as skills, tools, permissions, workspace context, and provider configuration must remain separate concerns rather than being mixed into the identity identifier.

### 3.3 Identity Validation

- Reject malformed UUID values.
- Reject empty required names and roles.
- Reject self-management relationships.
- Validate manager and division references when organizational registration is introduced.
- Do not silently generate a new identifier when restoring a persisted Agent.

## 4. BaseAgent Contract

`BaseAgent` remains the abstract foundation for all agents.

Responsibilities:

- Store Agent identity metadata.
- Expose a stable, read-only `agent_id`.
- Provide the abstract `run(task)` execution contract.
- Preserve optional `BaseMemory` integration.
- Provide `remember()` and `recall()` methods.
- Provide a foundation for future lifecycle and execution metadata.

Compatibility requirements:

- Preserve the existing positional constructor arguments: `name`, `role`, and `memory`.
- Add new optional parameters without breaking existing callers.
- Preserve the current behavior when memory is not configured.
- Preserve existing memory behavior during the first migration stage.
- Keep `ProductManagerAgent` provider injection, conversation memory, context engineering, and token budgeting operational.

Memory key migration from name-based namespaces to permanent Agent identifiers must be handled separately with an explicit compatibility strategy. It must not silently make existing memory inaccessible.

## 5. BaseDivision Contract

`BaseDivision` represents an organizational unit.

Planned responsibilities:

- Maintain a stable `division_id`.
- Store division name, description, and manager reference.
- Track registered Agent membership.
- Validate membership and manager relationships.
- Prevent duplicate membership.
- Support controlled Agent assignment and removal.

Division identifiers should use stable, unique slugs such as `engineering_technology`. Display names may change without changing the identifier.

A Division must not directly execute Agent tasks. Execution belongs to the Orchestrator.

## 6. AgentRegistry Contract

`AgentRegistry` is responsible for Agent registration and lookup.

Primary responsibilities:

- Register agents using `agent_id`.
- Retrieve agents by `agent_id`.
- Reject duplicate identifiers.
- Unregister agents through explicit operations.
- List registered agents.
- Support secondary name lookup for backward compatibility.
- Detect ambiguous name lookups rather than selecting an arbitrary Agent.

The registry must not execute tasks or manage LLM generation.

## 7. DivisionRegistry Contract

`DivisionRegistry` is responsible for Division registration and lookup.

Responsibilities:

- Register divisions using `division_id`.
- Retrieve divisions by identifier.
- Reject duplicate division identifiers.
- List registered divisions.
- Validate Agent membership references.
- Support future workspace-scoped organizational structures.

The registry must not execute workflows or generate AI responses.

## 8. Orchestrator Contract

The Orchestrator coordinates Agent execution.

Responsibilities:

- Resolve an Agent through AgentRegistry.
- Validate execution requests.
- Delegate tasks to the selected Agent.
- Return execution results.
- Provide a future extension point for task routing, coordination, and execution tracking.

Compatibility requirements:

- Preserve the existing `execute(agent_name, task)` behavior during migration.
- Preserve name-based registration and lookup through a compatibility interface.
- Keep existing `register_agent()`, `list_agents()`, and `execute()` callers operational until migration is complete.
- Do not introduce automatic multi-agent execution in the initial registry migration.

The Orchestrator must not become a replacement for AgentRegistry or DivisionRegistry.

## 9. AgentMessageBus Contract

`AgentMessageBus` is a future internal communication component.

Its responsibilities may include:

- Message delivery between Agents.
- Sender and recipient identification through Agent IDs.
- Message correlation identifiers.
- Message metadata and timestamps.
- Message validation and routing.

It is separate from external integrations such as Telegram, email, and social platforms.

MessageBus implementation is scheduled after the identity, registry, and orchestration foundations are stable.

## 10. Target Module Boundaries

Planned structure:

    app/
    ├── agents/
    │   ├── base_agent.py
    │   ├── product_manager.py
    │   └── managers/
    ├── divisions/
    │   └── base_division.py
    └── core/
        ├── agent_registry.py
        ├── division_registry.py
        ├── orchestrator.py
        └── message_bus.py

Existing modules must be retained during migration. New modules should be introduced incrementally.

## 11. Existing Compatibility Requirements

The following behaviors are existing regression requirements:

### BaseAgent

- Existing constructor calls remain valid.
- `run(task)` remains abstract.
- Memory remains optional.
- `remember()` and `recall()` retain their current behavior.
- Missing memory configuration raises RuntimeError.

### AgentOrchestrator

- Agent registration remains supported.
- Duplicate registrations are rejected.
- Empty names are rejected.
- Name lookup remains case-insensitive during migration.
- `list_agents()` preserves its existing output contract until callers are migrated.
- Existing ProductManagerAgent execution remains operational.

### ProductManagerAgent

Preserve:

- LLM provider dependency injection.
- Optional persistent memory.
- Conversation memory and session isolation.
- Recent conversation history.
- Relevant conversation retrieval.
- Project context.
- Prompt character limits.
- Token budget enforcement.
- Context priority and trimming behavior.
- Existing validation and response persistence behavior.

## 12. Migration Roadmap

| Milestone | Scope |
|---|---|
| M37 | Architecture specification and compatibility contract |
| M38 | Agent Identity and BaseAgent evolution |
| M39 | BaseDivision and DivisionRegistry |
| M40 | AgentRegistry |
| M41 | Orchestrator evolution |
| M42 | AgentMessageBus foundation |
| M43 | Integration and regression testing |

The roadmap may be adjusted when implementation findings require it. Changes must be documented.

## 13. Testing Strategy

Every implementation milestone must include:

- Unit tests for new behavior.
- Regression tests for existing behavior.
- Invalid input and duplicate registration tests.
- Identity stability tests.
- Integration tests when components interact.
- Full test-suite execution before completion.

Primary existing test files:

- `tests/test_base_agent.py`
- `tests/test_orchestrator.py`
- `tests/test_product_manager.py`

Full regression command:

    python -m unittest discover -s tests -v

## 14. Definition of Done

M37 is complete when:

- Agent identity rules are documented.
- Core component responsibilities are documented.
- Module boundaries are documented.
- Existing compatibility requirements are documented.
- Migration order is documented.
- Testing requirements are documented.
- The architecture specification is reviewed and committed.

## 15. Final Architecture Decision

The AI Super App will use UUID v4 as the permanent identity format for Agents.

Agent names, formal titles, roles, divisions, and manager assignments are organizational metadata, not permanent identity.

The existing Agentic Content Creator implementation will evolve incrementally into the AI Super App foundation. A wholesale rewrite is explicitly avoided.

## 16. Additional Architecture Clarifications

### 16.1 UUID Generation and Restoration

- Generate UUID v4 exactly once when a new Agent identity is created.
- Validate explicitly supplied identifiers as UUID version 4.
- Treat restored identifiers as persisted identity data, not new identity creation.
- Never silently replace an existing identifier during restoration.
- Expose `agent_id` as read-only after initialization.
- Identity restoration must preserve the original identifier.

### 16.2 Memory Namespace Migration

The current memory implementation uses Agent names as memory namespaces.

Migration to Agent ID namespaces must be gradual and backward-compatible.

Requirements:

- Preserve access to existing name-based memory entries.
- Introduce an explicit migration or compatibility lookup strategy.
- Avoid silently creating empty Agent ID namespaces when legacy data exists.
- Prevent accidental cross-Agent memory access.
- Add tests for legacy memory retrieval and migrated memory behavior.
- Do not change the current memory namespace behavior in M38 without a verified migration strategy.

### 16.3 Registry Ownership and Orchestrator Boundaries

AgentRegistry is the single owner of in-memory Agent registration and lookup.

Orchestrator delegates Agent resolution to AgentRegistry and coordinates execution.

Requirements:

- Avoid maintaining duplicate Agent registries in Orchestrator.
- Preserve legacy public methods through delegation or a compatibility adapter.
- Keep registration validation inside AgentRegistry.
- Keep task execution and coordination inside Orchestrator.
- Ensure registry lookup behavior is deterministic.
- Reject ambiguous name-based lookup requests.

### 16.4 Identity and Organization Boundaries

Agent identity, organizational membership, and execution configuration are separate concepts.

- Agent ID identifies the Agent permanently.
- Division ID identifies an organizational unit.
- Manager Agent ID identifies a reporting relationship.
- Workspace ID identifies the workspace context when multi-workspace support is introduced.
- Provider configuration, skills, tools, and permissions remain independently managed capabilities.

Organizational reassignment must not change permanent Agent identity.

## 17. Architecture Review Checklist

Before implementation begins, verify:

- [ ] Agent ID is independent of display name and role.
- [ ] UUID v4 generation and restoration rules are explicit.
- [ ] Existing Agent constructors remain compatible.
- [ ] Existing memory data remains accessible.
- [ ] AgentRegistry owns Agent registration.
- [ ] DivisionRegistry owns Division registration.
- [ ] Orchestrator delegates lookup rather than duplicating registry state.
- [ ] ProductManagerAgent dependency injection remains supported.
- [ ] Existing regression tests remain mandatory.
- [ ] Migration is incremental and documented.
