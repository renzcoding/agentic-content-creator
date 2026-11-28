# M45 — Multi-Provider & Intelligent Model Routing Foundation

## 1. Overview

M45 introduces a foundational multi-provider, multi-model, and intelligent model-routing layer while preserving the existing `BaseLLMProvider` contract.

The implementation is designed to support local-first AI execution, optional cloud providers, model selection, health checks, bounded retries, fallback, usage tracking, and budget preflight checks.

The milestone builds on the stable M44 foundation without replacing the existing Ollama integration.

## 2. Baseline and Compatibility

M44 baseline:
- Commit: `5705d0a`
- Branch: `main`
- Existing test baseline: 284 tests passed.

Backward compatibility requirements:
- Preserve `BaseLLMProvider.generate(prompt) -> str`.
- Keep `OllamaProvider` available.
- Keep `OllamaService` available.
- Preserve the existing ProductManagerAgent default provider behavior.
- Avoid changing unrelated agent and content-generation workflows.

## 3. Architecture

The M45 routing foundation consists of the following components:

| Component | Responsibility |
|---|---|
| `BaseLLMProvider` | Existing provider abstraction |
| `ModelConfiguration` | Model identity, provider, capabilities, availability, approval, context and pricing configuration |
| `ModelRegistry` | In-memory model registration and lookup |
| `ModelSelectionPolicy` | Manual and automatic model candidate selection |
| `ModelHealthChecker` | Model health evaluation through an injected callback |
| `ModelUsageTracker` | In-memory request, token and estimated-cost tracking |
| `ModelBudgetManager` | Estimated-cost budget preflight checks |
| `ModelRouter` | Provider selection, generation, retry, fallback and usage recording |

### 3.1 ModelConfiguration

Defines the configuration of an individual model.

Responsibilities:
- Validate model and provider identifiers.
- Store enabled and local-model flags.
- Store capabilities and approval requirements.
- Store optional context-window information.
- Validate optional input and output pricing.

### 3.2 ModelRegistry

Provides in-memory model registration and lookup.

Supported operations include:
- Register a model.
- Retrieve a model by ID.
- Unregister a model.
- List registered models.
- List enabled models.
- Retrieve models by provider.

Duplicate model IDs are rejected.

Persistence is not implemented in this milestone.

### 3.3 ModelSelectionPolicy

Supports manual and automatic candidate selection.

Selection considerations:
- Model enabled status.
- Required capabilities.
- Local-first prioritization.
- Explicit approval for cloud or approval-required models.
- Preferred model selection.
- Registry ordering.

Local models that do not require approval can be selected automatically. Non-local models and models requiring approval must be included in the approved model IDs.

### 3.4 ModelHealthChecker

Evaluates model availability through an injected health-check callback.

Behavior:
- Disabled models are considered unhealthy.
- Callback exceptions are treated as unhealthy results.
- Non-boolean callback results raise `TypeError`.

The component does not implement provider-specific network health checks by itself.

### 3.5 ModelUsageTracker

Tracks successful model usage in memory.

Tracked information includes:
- Request count.
- Estimated input tokens.
- Estimated output tokens.
- Estimated cost.

Unknown or incomplete pricing does not get interpreted as free usage. Estimated cost becomes unknown when the available pricing information is insufficient.

Persistent usage storage and detailed per-request audit history are not included.

### 3.6 ModelBudgetManager

Performs estimated-cost budget preflight checks.

The estimate considers:
- Input token estimates.
- Reserved maximum output tokens.
- Configured input-token pricing.
- Configured output-token pricing.
- Existing tracked usage.
- The applicable model budget.

When budget enforcement applies:
- Missing or incomplete model pricing raises `ValueError` because the request cost cannot be estimated reliably.
- Unknown historical usage cost raises `BudgetExceededError` because the existing budget consumption cannot be verified.
- A request whose estimated total exceeds its configured budget raises `BudgetExceededError`.

These checks fail closed: unknown costs are never interpreted as free usage. Automatic routing can skip candidates rejected with `BudgetExceededError`; configuration errors such as missing pricing are propagated.

Important limitation: this is a preflight estimate, not an atomic reservation. Concurrent requests can exceed the configured budget.

### 3.7 ModelRouter

`ModelRouter` implements `BaseLLMProvider` and preserves the existing generation interface:

```python
response = model_router.generate(prompt)
Its responsibilities include:
1. Validate the prompt.
2. Reset previous selection metadata.
3. Obtain candidate models from the selection policy.
4. Check model health.
5. Resolve the configured provider.
6. Perform budget preflight when enabled.
7. Generate a response.
8. Validate the generated response.
9. Retry failures within the configured limit.
10. Fall back to other eligible candidates when appropriate.
11. Record successful usage.
12. Expose the selected model ID.
Important behavior:
- Failed generation attempts are not recorded as successful usage.
- Usage-tracking failures do not trigger another generation attempt.
- Automatic selection can skip a model that exceeds its budget.
- A manually preferred model that exceeds its budget raises the budget exception.
- Retry attempts are bounded by configuration.
- Empty or invalid provider responses are rejected.
max_output_tokens is used for budget estimation. The current provider contract does not enforce an actual generation output-token limit.
4. ProductManagerAgent Integration
The existing ProductManagerAgent accepts an optional injected provider.

Its provider contract remains compatible with BaseLLMProvider.

Conceptually:
agent = ProductManagerAgent(provider=model_router)



When a provider is injected, the agent delegates generation to that provider. When no provider is injected, it retains the existing OllamaProvider default.

The integration test verifies:
- ModelRouter can be injected into ProductManagerAgent.
- The agent delegates prompt generation.
- The generated response is returned.
- The selected model can be inspected.
- Successful usage is tracked.
This is an integration test proving dependency-injection compatibility. It is not yet centralized production configuration for every agent.

BaseAgent remains unchanged and does not directly depend on ModelRouter.
5. Existing Ollama Integration
The existing Ollama implementation remains available.

Preserved components:
- BaseLLMProvider
- OllamaProvider
- OllamaService
- Existing OLLAMA_MODEL configuration
The existing ScriptGenerator still uses its direct Ollama integration. It has not been migrated to ModelRouter in this milestone to avoid destabilizing the established content-generation workflow.
6. Security and Approval Considerations
The routing foundation supports an explicit approved-model ID allowlist.

Approval rules:
- Local models that do not require approval can be selected automatically.
- Cloud/non-local models require explicit approval.
- Models marked as requiring approval require explicit approval.
- A model not included in the approved list must not be selected when approval is required.
This is a model-selection safeguard, not a complete interactive user-approval workflow.

Provider credentials, secrets management, and cloud-provider authorization flows remain future work.
7. Testing and Validation
M45 test coverage includes:
- test_model_configuration.py
- test_model_registry.py
- test_model_selection_policy.py
- test_model_health_checker.py
- test_model_usage_tracker.py
- test_model_budget_manager.py
- test_model_router.py
- test_model_router_integration.py
- test_model_router_integration.py covers ProductManagerAgent dependency-injection compatibility and is discovered separately from test_model_router.py.
Recorded validation checkpoint:
- Full unit test suite: 378 tests passed.
- Python compilation check: python -m compileall -q app tests passed.
These results describe the recorded checkpoint and must be rerun after subsequent code or documentation changes.
8. Architecture Decisions
1. Preserve BaseLLMProvider.generate(prompt) -> str to maintain compatibility.
2. Keep ModelRouter as a provider implementation rather than coupling routing logic to BaseAgent.
3. Inject providers through the existing ProductManagerAgent provider dependency.
4. Keep model registry and usage tracking in memory for the initial foundation.
5. Prioritize local models to support local-first execution.
6. Require explicit approval for cloud and approval-required models.
7. Use bounded retries and fallback to avoid uncontrolled generation attempts.
8. Fail closed when budget enforcement cannot reliably estimate cost.
9. Keep ScriptGenerator's existing Ollama path unchanged until a dedicated migration is planned.
9. Implementation Status
Capability	Status
Model configuration	Implemented
In-memory model registry	Implemented
Manual model selection	Implemented
Automatic model selection	Implemented
Local-first prioritization	Implemented
Capability filtering	Implemented
Model approval allowlist	Implemented
Callback-based health checking	Implemented
In-memory usage tracking	Implemented
Budget preflight estimation	Implemented
Bounded retry and fallback	Implemented
ModelRouter provider compatibility	Implemented
ProductManagerAgent provider injection	Implemented and integration-tested
Centralized per-agent model configuration	Pending
Persistent model registry	Pending
Persistent usage and cost history	Pending
Interactive approval workflow	Pending
Production cloud-provider adapters	Pending
ScriptGenerator migration	Pending
Atomic budget reservation	Pending
Actual provider cost reconciliation	Pending
Enforced output-token limits	Pending

10. Follow-up Work
Potential follow-up milestones should address:
1. Centralized per-agent model configuration.
2. Persistent model and provider configuration.
3. Production-ready provider adapters.
4. Secure credential and secret management.
5. Interactive cloud-model approval.
6. Persistent usage and cost auditing.
7. Atomic budget reservation and reconciliation.
8. Provider-enforced output limits.
9. Controlled migration of ScriptGenerator to ModelRouter.
10. End-to-end tests using configured providers.
11. Completion Checklist
- [x] Preserve the existing BaseLLMProvider contract.
- [x] Introduce model configuration.
- [x] Introduce model registry.
- [x] Introduce manual and automatic selection policies.
- [x] Introduce model health checking.
- [x] Introduce usage tracking.
- [x] Introduce budget preflight checks.
- [x] Introduce ModelRouter with bounded retry and fallback.
- [x] Add model approval filtering.
- [x] Verify ProductManagerAgent dependency injection.
- [x] Add unit and integration tests.
- [ ] Complete final source and architecture review.
- [ ] Rerun the full test suite after final changes.
- [ ] Review Git diff and working-tree status.
- [ ] Commit and push the completed milestone.
12. Final Notes
M45 establishes the first reusable model-routing foundation for the Agentic Content Creator project.

It does not yet represent a complete production multi-provider platform. Persistent configuration, production cloud adapters, centralized agent configuration, interactive approval, and reliable budget reservation remain explicit future improvements.

The priority is to preserve the stable M44 foundation while creating a clean extension point for future providers, models, agents, and intelligent routing policies.
