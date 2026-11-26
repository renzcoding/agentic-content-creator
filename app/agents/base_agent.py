from abc import ABC, abstractmethod
from uuid import UUID, uuid4

from app.memory.base_memory import BaseMemory


class BaseAgent(ABC):
    """Define the standard interface for all AI agents."""

    def __init__(
        self,
        name: str,
        role: str,
        memory: BaseMemory | None = None,
        agent_id: str | None = None,
        formal_name: str | None = None,
        division_id: str | None = None,
        manager_agent_id: str | None = None,
    ) -> None:
        """Initialize permanent identity and optional organizational metadata."""

        # Validate required identity fields before processing them.
        if not isinstance(name, str) or not name.strip():
            raise ValueError("Agent name must be a non-empty string.")

        if not isinstance(role, str) or not role.strip():
            raise ValueError("Agent role must be a non-empty string.")

        # Validate the optional memory dependency against its shared contract.
        if memory is not None and not isinstance(memory, BaseMemory):
            raise TypeError("Memory must implement BaseMemory.")

        # Validate optional organizational metadata.
        for field_name, field_value in (
            ("formal_name", formal_name),
            ("division_id", division_id),
        ):
            if field_value is not None:
                if not isinstance(field_value, str):
                    raise TypeError(f"{field_name} must be a string or None.")

                if not field_value.strip():
                    raise ValueError(f"{field_name} must not be empty.")

        # Validate the optional manager identifier as a UUID.
        if manager_agent_id is not None:
            if not isinstance(manager_agent_id, str):
                raise TypeError("Manager agent ID must be a string or None.")

            try:
                manager_agent_id = str(UUID(manager_agent_id))
            except ValueError as error:
                raise ValueError("Manager agent ID must be a valid UUID.") from error

        self.name = name.strip()
        self.role = role.strip()
        self.memory = memory

        # Generate a permanent UUID v4 or restore an existing valid identity.
        if agent_id is not None and not isinstance(agent_id, str):
            raise TypeError("Agent ID must be a string or None.")

        try:
            parsed_agent_id = UUID(agent_id) if agent_id is not None else uuid4()
        except ValueError as error:
            raise ValueError("Agent ID must be a valid UUID.") from error

        if parsed_agent_id.version != 4:
            raise ValueError("Agent ID must be a valid UUID version 4.")

        self._agent_id = str(parsed_agent_id)

        # Store validated organizational metadata.
        self.formal_name = formal_name.strip() if formal_name is not None else None
        self.division_id = division_id.strip() if division_id is not None else None
        self.manager_agent_id = manager_agent_id

    @property
    def agent_id(self) -> str:
        """Return the permanent, read-only agent identifier."""
        return self._agent_id

    def remember(self, key: str, value: str) -> None:
        """Store information using an agent-specific memory key."""
        if self.memory is None:
            raise RuntimeError("Memory is not configured for this agent.")

        memory_key = f"{self.name}:{key}"
        self.memory.save(memory_key, value)

    def recall(self, key: str) -> str | None:
        """Retrieve information using an agent-specific memory key."""
        if self.memory is None:
            raise RuntimeError("Memory is not configured for this agent.")

        memory_key = f"{self.name}:{key}"
        return self.memory.retrieve(memory_key)

    @abstractmethod
    def run(self, task: str) -> str:
        """Execute a task and return the agent's result."""
        raise NotImplementedError
