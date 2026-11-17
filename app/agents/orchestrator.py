
from app.agents.base_agent import BaseAgent


class AgentOrchestrator:
    """Manage agent registration and task execution."""

    def __init__(self) -> None:
        """Initialize an empty agent registry."""
        self.agents: dict[str, BaseAgent] = {}

    def register_agent(self, agent: BaseAgent) -> None:
        """Register an agent using its name as the registry key."""

        # Normalize the agent name for consistent lookup.
        agent_key = agent.name.strip().lower()

        if not agent_key:
            raise ValueError("Agent name must not be empty.")

        if agent_key in self.agents:
            raise ValueError(f"Agent '{agent.name}' is already registered.")

        self.agents[agent_key] = agent

    def list_agents(self) -> list[dict[str, str]]:
        """Return the names and roles of all registered agents."""

        # Build a readable summary of the registered agents.
        return [
            {
                "name": agent.name,
                "role": agent.role,
            }
            for agent in self.agents.values()
        ]

    def execute(self, agent_name: str, task: str) -> str:
        """Find an agent and execute the requested task."""

        # Normalize the requested name before searching.
        agent_key = agent_name.strip().lower()

        if not agent_key:
            raise ValueError("Agent name must not be empty.")

        if agent_key not in self.agents:
            raise ValueError(f"Agent '{agent_name}' is not registered.")

        return self.agents[agent_key].run(task)
