# M39 — BaseDivision and DivisionRegistry Implementation

## 1. Overview

Milestone M39 implements the organizational Division foundation defined in M37.

It introduces two components:

- `BaseDivision`: represents an organizational unit and manages its Agent membership and manager relationship.
- `DivisionRegistry`: owns Division registration, retrieval, listing, and validation of Agent references.

This milestone establishes organizational structure without introducing Agent registration, task execution, workflow orchestration, or AI decision-making.

## 2. Architectural Position

The organizational model distinguishes three separate concepts:

- Agent: an individual execution and decision-making unit.
- Division: an organizational unit that groups Agents by responsibility.
- Registry: the component responsible for managing registered objects and their lookup.

M39 implements only the Division side of this model.

The intended relationship is:

1. A Division has a stable `division_id`.
2. A Division can contain multiple Agent IDs.
3. A Division can designate one of its members as its manager.
4. A DivisionRegistry manages registered Division instances.
5. Agent existence is validated against an externally supplied collection of Agent IDs.

The Division does not own or instantiate Agents. AgentRegistry is planned for M40.

## 3. Files Created

### 3.1 `app/divisions/__init__.py`

Declares the Division package.

It currently contains a package-level module docstring and does not expose additional behavior.

### 3.2 `app/divisions/base_division.py`

Defines `BaseDivision`, the base organizational unit.

#### Constructor

`BaseDivision(division_id, name, description="")`

Parameters:

- `division_id`: permanent lowercase snake-case identifier.
- `name`: human-readable Division name.
- `description`: optional descriptive text.

Validation:

- Division ID must match the lowercase slug pattern.
- Division name must be a non-empty string after trimming.
- Description must be a string.

The identifier is stored internally as `_division_id` and exposed through a read-only property.

#### Properties

- `division_id`: returns the permanent Division identifier.
- `agent_ids`: returns a sorted tuple of member Agent IDs. Returning a tuple prevents callers from directly modifying internal membership.
- `manager_agent_id`: returns the current manager Agent ID or `None`.

#### Methods

`has_agent(agent_id)`

Checks whether the specified Agent ID belongs to the Division.

Returns a boolean.

`assign_agent(agent_id)`

Adds an Agent ID to the Division.

The ID must be a valid UUID version 4. Duplicate membership is rejected.

Returns `None` when successful.

`remove_agent(agent_id)`

Removes an existing Agent membership.

The operation is rejected when the Agent is not a member or is still the current manager.

The manager relationship must first be released or changed.

Returns `None` when successful.

`set_manager(agent_id)`

Assigns a Division manager.

The selected Agent must already belong to the Division. Passing `None` releases the manager relationship.

Only one manager reference is stored at a time.

Returns `None` when successful.

`_validate_agent_id(agent_id)`

Private static validation method.

It parses the supplied identifier as a UUID and requires UUID version 4.

Invalid identifiers raise `ValueError`.

## 4. Division Identifier Rules

Division IDs are stable organizational identifiers.

Examples:

- `strategy_research`
- `content_development`
- `creative_production`
- `publishing_distribution`
- `analytics_growth`
- `monetization_business`
- `quality_governance`
- `engineering_technology`
- `automation_integration`

The identifier is separate from the display name.

A display name can be updated independently in a future feature without changing the Division's identity.

The current implementation makes `division_id` read-only through a property without a setter.

## 5. Agent Membership Rules

Membership is stored as Agent UUID strings rather than references to Agent objects.

This keeps Division independent from Agent construction and AgentRegistry implementation.

Rules:

1. Every membership identifier must be a UUID version 4.
2. An Agent cannot be assigned twice to the same Division.
3. Only existing members can be removed.
4. A current manager cannot be removed until the manager relationship is released.
5. The public membership property returns an immutable tuple.

The internal membership collection is a set, preventing duplicate identifiers.

The public property sorts the identifiers for deterministic output.

## 6. Manager Relationship

A Division may have one manager Agent.

The manager must already be a member of that Division.

The manager relationship is represented by `manager_agent_id`.

Passing `None` to `set_manager` releases the relationship.

Removing the current manager without first releasing or changing the relationship is rejected.

This milestone does not implement manager hierarchy, reporting chains, delegation, or manager permissions.

Those responsibilities belong to future organizational and orchestration components.

## 7. DivisionRegistry

File: `app/divisions/division_registry.py`

`DivisionRegistry` is responsible for managing registered Division instances.

Its internal collection is a dictionary keyed by `division_id`.

### Constructor

`DivisionRegistry()`

Initializes an empty registry.

### Methods

`register(division)`

Registers a `BaseDivision` instance.

Rejects objects of other types and duplicate Division IDs.

Returns `None` when successful.

`get(division_id)`

Retrieves a Division by its stable identifier.

Returns the Division instance when found, otherwise `None`.

`list_divisions()`

Returns all registered Division instances in registration order.

The returned list is a separate list, not the registry's internal dictionary.

`validate_agent_references(agent_ids)`

Checks that all Agent IDs referenced by registered Divisions exist in the supplied collection.

It validates both membership references and manager references.

An unknown reference raises `ValueError`.

The manager check is retained explicitly to make the registry's reference-validation contract clear, even though BaseDivision already requires a manager to be a member.

The method does not register Agents or modify Division membership.

## 8. Error Handling

The implementation uses:

- `ValueError` for invalid identifiers, duplicate registration or membership, invalid manager relationships, and unknown Agent references.
- `TypeError` when an API receives an object of an unexpected type.
- `AttributeError` when callers attempt to assign to the read-only `division_id` property.

Errors are raised immediately rather than silently changing organizational state.

## 9. Test Coverage

Files:

- `tests/test_base_division.py`
- `tests/test_division_registry.py`

### BaseDivision tests

The tests cover:

- Division metadata initialization.
- Read-only Division ID.
- Invalid Division ID rejection.
- Empty Division name rejection.
- Agent membership assignment.
- Duplicate membership rejection.
- Invalid Agent UUID rejection.
- Membership removal.
- Non-member removal rejection.
- Manager assignment.
- Manager membership validation.
- Manager relationship release.
- Prevention of removing the current manager.

### DivisionRegistry tests

The tests cover:

- Division registration and retrieval.
- Duplicate Division ID rejection.
- Unknown Division lookup.
- Listing registered Divisions.
- Successful Agent reference validation.
- Unknown membership reference rejection.
- Unknown manager reference rejection.

M39-specific tests: 20 BaseDivision and 7 DivisionRegistry tests.

## 10. Regression Verification

Full test command:

`python -m unittest discover -s tests -v`

Latest result after the M39 implementation and coupling cleanup:

- Total tests: 185
- Passed: 185
- Failed: 0

Whitespace and patch validation:

`git diff --check`

Latest result: no reported issues.

## 11. Design Decisions

### Stable identifiers

Division IDs are permanent identifiers, not display labels.

This makes them suitable for future references from Agents, tasks, workflows, configuration, and persistent storage.

### UUID-based membership

Division stores Agent IDs instead of Agent instances.

This avoids direct coupling to BaseAgent and allows AgentRegistry to remain the single owner of Agent registration in M40.

### Registry ownership

DivisionRegistry owns Division registration and lookup.

BaseDivision owns only its internal membership and manager relationship.

### No task execution

A Division is an organizational structure, not an execution engine.

Task execution and delegation remain responsibilities of the Orchestrator and future workflow components.

### No persistence yet

The registry is currently in-memory.

Database persistence, workspace-scoped registration, and restoration are outside M39 scope.

## 12. Explicit Scope Boundaries

M39 does not implement:

- AgentRegistry.
- Agent registration or unregistration.
- Agent name lookup.
- Orchestrator integration.
- Agent-to-Agent messaging.
- Division task execution.
- Workflow execution.
- Workspace-level persistence.
- Database models or migrations.
- Manager delegation and reporting hierarchy.
- Permission enforcement.

These boundaries prevent M39 from taking responsibilities assigned to later milestones.

## 13. Relationship to the Roadmap

M37 defines the architecture and implementation sequence.

M38 establishes permanent Agent identity and evolves BaseAgent.

M39 establishes Division identity, membership, manager relationships, and DivisionRegistry.

The next milestone is:

**M40 — AgentRegistry**

M40 will introduce the central owner of Agent registration and lookup using permanent Agent IDs.

Later milestones will connect AgentRegistry, DivisionRegistry, and Orchestrator while preserving their separate responsibilities.

## 14. Definition of Done

- [x] BaseDivision implemented.
- [x] Stable Division ID validation.
- [x] Read-only Division identifier.
- [x] Agent membership management.
- [x] Manager relationship validation.
- [x] DivisionRegistry implemented.
- [x] Duplicate Division registration rejected.
- [x] Division lookup and listing implemented.
- [x] Agent references validated.
- [x] Unit tests added.
- [x] Full regression suite passed.
- [x] Patch whitespace validation passed.
- [x] Implementation documented.

Commit and remote synchronization are tracked separately from implementation verification.
