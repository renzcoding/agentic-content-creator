from app.agents.base_agent import BaseAgent
from app.core.agent_registry import AgentRegistry


class AgentOrchestrator:
    """Coordinate Agent registration and task execution."""

    def __init__(self, registry: AgentRegistry | None = None) -> None:
        """Initialize the Orchestrator with an AgentRegistry."""
        self.registry = registry or AgentRegistry()

    @property
    def agents(self) -> dict[str, BaseAgent]:
        """Provide a legacy name-keyed view of registered Agents."""
        return {
            agent.name.strip().lower(): agent
            for agent in self.registry.list_agents()
        }

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an Agent while preserving legacy name validation."""
        if not isinstance(agent, BaseAgent):
            raise TypeError("Only BaseAgent instances can be registered.")

        existing_agent = self.registry.get_by_name(agent.name)

        if existing_agent is not None:
            raise ValueError(
                f"Agent '{agent.name}' is already registered."
            )

        self.registry.register(agent)

    def list_agents(self) -> list[dict[str, str]]:
        """Return the names and roles of all registered Agents."""
        return [
            {
                "name": agent.name,
                "role": agent.role,
            }
            for agent in self.registry.list_agents()
        ]

    def execute(self, agent_name: str, task: str) -> str:
        """Find an Agent through the registry and execute its task."""
        normalized_name = agent_name.strip()

        if not normalized_name:
            raise ValueError("Agent name must not be empty.")

        agent = self.registry.get_by_name(normalized_name)

        if agent is None:
            raise ValueError(
                f"Agent '{agent_name}' is not registered."
            )

        return agent.run(task)
