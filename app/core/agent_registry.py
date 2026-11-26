from app.agents.base_agent import BaseAgent


class AgentRegistry:
    """Manage Agent registration, lookup, and lifecycle."""

    def __init__(self) -> None:
        """Initialize an empty Agent registry."""
        self._agents: dict[str, BaseAgent] = {}

    def register(self, agent: BaseAgent) -> None:
        """Register an Agent using its permanent identifier."""
        if not isinstance(agent, BaseAgent):
            raise TypeError("Only BaseAgent instances can be registered.")

        if agent.agent_id in self._agents:
            raise ValueError(
                f"Agent ID '{agent.agent_id}' is already registered."
            )

        self._agents[agent.agent_id] = agent

    @staticmethod
    def _validate_agent_id(agent_id: str) -> str:
        """Validate and normalize an Agent identifier."""
        if not isinstance(agent_id, str):
            raise TypeError("Agent ID must be a string.")

        normalized_id = agent_id.strip()
        if not normalized_id:
            raise ValueError("Agent ID must not be empty.")

        return normalized_id

    def get(self, agent_id: str) -> BaseAgent | None:
        """Retrieve an Agent by its permanent identifier."""
        normalized_id = self._validate_agent_id(agent_id)
        return self._agents.get(normalized_id)

    def unregister(self, agent_id: str) -> BaseAgent | None:
        """Remove and return an Agent by its permanent identifier."""
        normalized_id = self._validate_agent_id(agent_id)
        return self._agents.pop(normalized_id, None)

    def list_agents(self) -> list[BaseAgent]:
        """Return all registered Agents in insertion order."""
        return list(self._agents.values())

    def get_by_name(self, name: str) -> BaseAgent | None:
        """Retrieve an Agent by name and reject ambiguous matches."""
        if not isinstance(name, str):
            raise TypeError("Agent name must be a string.")

        normalized_name = name.strip().lower()

        if not normalized_name:
            raise ValueError("Agent name must not be empty.")

        matches = [
            agent
            for agent in self._agents.values()
            if agent.name.strip().lower() == normalized_name
        ]

        if len(matches) > 1:
            raise ValueError(
                f"Agent name '{name}' is ambiguous."
            )

        return matches[0] if matches else None
