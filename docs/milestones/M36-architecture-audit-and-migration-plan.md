# M36 - AI Super App Architecture Audit & Migration Plan

## Objective

Audit the current Agentic Content Creator architecture and define a safe migration path toward the AI Super App blueprint.

This milestone is for architecture review and planning only. No application code or directory structure is changed.

## Current Architecture Audit

### Agent Core

- `app/agents/base_agent.py`
  - Provides the abstract BaseAgent contract.
  - Supports agent identity through name and role.
  - Supports basic memory access.
  - Future improvements: stable agent ID, workspace context, permissions, lifecycle, and execution metadata.

- `app/agents/orchestrator.py`
  - Registers agents by normalized name.
  - Prevents duplicate names.
  - Provides basic agent listing and direct execution.
  - Future improvements: dedicated registries, task management, message bus, and execution tracking.

- `app/agents/product_manager.py`
  - Uses provider dependency injection.
  - Builds prompts using project context and conversation history.
  - Applies token estimation and context limits.
  - Future improvements: centralized context management, task IDs, workspace isolation, and model gateway integration.

### LLM Services

- `app/services/llm/base_provider.py`
  - Defines the provider abstraction.

- `app/services/llm/ollama_provider.py`
  - Adapts the Ollama service to the provider interface.

- `app/services/ollama_service.py`
  - Sends generation requests to the local Ollama API.
  - Handles basic request errors and timeout behavior.

Future improvements:
- ModelGateway and provider registry.
- Configurable endpoint, timeout, and generation settings.
- Provider health checks, retries, fallback, response validation, and usage tracking.

### Memory and Conversation Storage

- `app/memory/base_memory.py`
  - Defines the key-value memory contract.

- `app/memory/conversation_memory.py`
  - Manages conversation messages, history, and keyword retrieval.

- `app/memory/base_conversation_storage.py`
  - Defines the conversation storage contract.

- `app/memory/conversation_storage_factory.py`
  - Selects JSON or SQLite storage based on configuration.

- `app/memory/json_conversation_storage.py`
  - Supports lightweight JSON persistence and legacy data loading.

- `app/memory/sqlite_conversation_storage.py`
  - Supports SQLite persistence and validation.

- `app/memory/conversation_data_validator.py`
  - Validates conversation data structure.

- `app/memory/json_memory.py`
  - Provides simple JSON key-value memory persistence.

Future improvements:
- Workspace, agent, and session isolation.
- Message IDs and timestamps.
- Incremental database writes.
- Structured and semantic memory.
- More scalable persistence.

### Utilities and Configuration

- `app/utils/token_estimator.py`
  - Provides approximate token estimation.
  - Future improvements: model-specific tokenization or provider usage data.

- `config/settings.py`
  - Contains current model, storage, and prompt configuration.
  - Future improvements: environment-based configuration and separation of development and production settings.

### Content Tools

- `app/tools/niche_planner.py`
  - Provides niche-specific content planning.
  - Future improvements: configurable niches and workspace-specific strategies.

- `app/tools/script_generator.py`
  - Generates and revises scripts using niche-aware prompt builders.
  - Future improvements: separate prompt construction, generation, and evaluation services.

- `app/tools/quality_checker.py`
  - Provides deterministic rule-based script validation.
  - Future improvements: categorized issues, structured scores, and a separate AI evaluation layer.

- `app/tools/visual_asset_agent.py`
  - Provides scene planning, visual descriptions, and duration estimates.
  - Future improvements: visual planning service, asset metadata, and production status.

- `app/tools/voice_asset_agent.py`
  - Provides local eSpeak NG voice generation.
  - Future improvements: TTS provider abstraction, voice profiles, and audio metadata.

- `app/tools/output_manager.py`
  - Exports content to JSON, Markdown, and text.
  - Future improvements: unique artifact IDs, atomic writes, and centralized file storage.

- `app/tools/content_history.py`
  - Reads and summarizes saved content history.
  - Future improvements: dedicated artifact storage and database-backed queries.

### Workflow

- `app/workflows/content_workflow.py`
  - Implements the current sequential content production workflow.
  - Includes quality checking, revision limits, output saving, and optional voice generation.
  - Future improvements: WorkflowEngine, structured workflow status, task IDs, progress tracking, approvals, retries, and persistence.

## Current Architecture Assessment

The current project is a working modular prototype with useful separation between agents, providers, memory, tools, and workflows.

The existing components should be reused where appropriate rather than rewritten from scratch.

The main architectural limitations are:
- Several tools are named as agents but do not have agent decision-making behavior.
- The workflow is tightly coupled to direct function calls and console output.
- Agent identity and organization are still basic.
- Workspace and customer isolation are not implemented.
- Persistence and artifact management are prototype-level.
- Social account management and publishing integrations are not yet implemented.
- Production monitoring, permissions, approval controls, and SaaS subscription management are not yet implemented.

## Target AI Super App Architecture

The target remains a Modular Monolith with migration-ready boundaries.

Core components planned:
- BaseAgent
- BaseDivision
- AgentRegistry
- DivisionRegistry
- Orchestrator
- AgentMessageBus
- WorkflowEngine
- TaskManager
- ModelGateway
- MemoryManager
- KnowledgeManager
- ToolRegistry
- PermissionManager
- EventManager
- EvaluationEngine
- MonitoringService

The organization will support:
- AI CEO / Executive Coordinator
- Division Managers
- Specialist Agents
- Shared AI Company Core

Agents will have stable identities, roles, responsibilities, skills, tools, permissions, and workspace context.

## Migration Plan

### Phase 1 - Documentation and Architecture Foundation

- Complete the architecture audit.
- Document the agreed AI Super App blueprint.
- Define module boundaries and dependency rules.
- Preserve the existing working content workflow.

### Phase 2 - Core Foundation

- Introduce stable agent identity.
- Build AgentRegistry and DivisionRegistry.
- Expand orchestration responsibilities.
- Introduce task and execution metadata.
- Add workspace context boundaries.

### Phase 3 - AI and Context Services

- Introduce ModelGateway.
- Preserve the existing BaseLLMProvider abstraction.
- Add provider configuration and health checks.
- Centralize prompt context and token budgeting.
- Improve memory and conversation persistence.

### Phase 4 - Workflow and Automation

- Introduce WorkflowEngine and TaskManager.
- Convert the current content workflow into a managed workflow.
- Add structured results, progress, retries, and approval states.
- Keep the current workflow usable during migration.

### Phase 5 - Content Production Core

- Build reusable content production pipelines.
- Support clipping, faceless content, animated content, and short-form video.
- Separate content planning, script generation, visual production, voice generation, and quality evaluation.

### Phase 6 - Publishing and Distribution

- Introduce Social Media Account Registry.
- Support multiple accounts and platforms per workspace.
- Prepare platform-specific content adaptations.
- Integrate official platform APIs where permitted.
- Support approval, scheduling, publishing status, retries, and audit logs.

### Phase 7 - Web App and Business Expansion

- Build the web application using the agreed stack.
- Add user and workspace management.
- Introduce subscription and usage management when the product is ready.
- Expand into creator SaaS, agency workflows, and digital products.

## Migration Rules

1. Do not rewrite working components without a clear reason.
2. Migrate incrementally and keep tests passing.
3. Avoid breaking existing content generation functionality.
4. Keep modules loosely coupled and reusable.
5. Add tests and milestone documentation for each meaningful change.
6. Preserve local-first AI with optional cloud providers.
7. Apply workspace isolation and permissions before customer-facing SaaS expansion.
8. Keep high-risk actions subject to approval.
9. Maintain compatibility with the current repository until the new foundation is stable.

## Milestone Definition of Done

- Current architecture has been audited.
- Reusable components and limitations are documented.
- Target architecture is recorded.
- Migration phases are defined.
- No application code has been changed during this audit.
- The next milestone can begin implementing the Core Foundation incrementally.

## Additional Blueprint Decisions

### Application and Business Direction

- Start with a Web App; consider Mobile after the web foundation is stable.
- Support Personal and UMKM users through isolated workspaces.
- Validate the internal AI Content Agency workflow before expanding into creator SaaS.
- Support future subscription-based services and digital products.
- Keep the current repository name until the new foundation is stable.

### Organization and Shared Core

The AI CEO / Executive Coordinator coordinates the organization and delegates work to Division Managers and Specialist Agents.

The initial organization includes these divisions:

1. Strategy & Research
2. Content Development
3. Creative Production
4. Publishing & Distribution
5. Analytics & Growth
6. Monetization & Business
7. Quality & Governance
8. Engineering & Technology
9. Automation & Integration

The organization uses a shared AI Company Core for reusable infrastructure and services.

### Architecture Layers

The target architecture is organized into:

1. Application Layer
2. Organization Layer
3. Agent Intelligence Layer
4. Workflow & Automation Layer
5. AI & Model Layer
6. Integration & Tool Layer
7. Data Layer
8. Governance & Operations Layer

### Technology Direction

- Backend: FastAPI
- Frontend: React, TypeScript, and Tailwind CSS
- Primary database: PostgreSQL
- Local development database: SQLite
- ORM: SQLAlchemy
- Local AI: Ollama through a provider abstraction
- Workflow engine: custom Python implementation initially
- API: REST
- Testing: unittest and integration tests
- Deployment: Linux, systemd, Nginx, and GitHub Actions

Cloud AI and cloud storage remain optional. Local-first operation is the default direction.

### Content Production and Distribution

The content system will use reusable production workflows for clipping, faceless content, animated content, and short-form video.

A master content package may be adapted for multiple selected social accounts. Adaptations can include aspect ratio, duration, captions, hashtags, metadata, thumbnails, and calls to action.

The Social Media Account Registry will support multiple accounts and platforms per workspace. Publishing will use official APIs where available and permitted, with approval controls, per-destination status, retries, audit logs, and credential protection.

### Autonomy and Governance

Automation may be triggered manually, on a schedule, by events, or through webhooks.

Autonomy levels will progress from assisted operation to controlled autonomy. High-risk actions require human approval. Automated execution must support permissions, budgets, timeouts, logging, pause controls, and emergency stop.

### Migration Principle

The current Agentic Content Creator remains the working prototype and migration starting point. Existing components will be reused where appropriate, and the new architecture will be introduced incrementally without prematurely replacing the current content workflow.
