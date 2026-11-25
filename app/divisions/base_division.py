import re
from uuid import UUID

class BaseDivision:
    """Represent an organizational unit and its Agent membership."""

    def __init__(
        self,
        division_id: str,
        name: str,
        description: str = "",
    ) -> None:
        """Initialize a Division with a stable slug identifier."""
        if not isinstance(division_id, str) or not re.fullmatch(
            r"[a-z][a-z0-9]*(?:_[a-z0-9]+)*",
            division_id,
        ):
            raise ValueError("Division ID must be a valid lowercase slug.")

        if not isinstance(name, str) or not name.strip():
            raise ValueError("Division name must not be empty.")

        if not isinstance(description, str):
            raise ValueError("Division description must be a string.")

        self._division_id = division_id
        self.name = name.strip()
        self.description = description
        self._agent_ids: set[str] = set()
        self._manager_agent_id: str | None = None

    @property
    def division_id(self) -> str:
        """Return the permanent, read-only Division identifier."""
        return self._division_id

    @property
    def agent_ids(self) -> tuple[str, ...]:
        """Return registered Agent IDs without exposing mutable membership."""
        return tuple(sorted(self._agent_ids))

    @property
    def manager_agent_id(self) -> str | None:
        """Return the Agent ID assigned as Division manager."""
        return self._manager_agent_id

    def has_agent(self, agent_id: str) -> bool:
        """Check whether an Agent belongs to this Division."""
        return agent_id in self._agent_ids

    def assign_agent(self, agent_id: str) -> None:
        """Add a valid Agent ID while preventing duplicate membership."""
        self._validate_agent_id(agent_id)

        if agent_id in self._agent_ids:
            raise ValueError("Agent is already a member of this Division.")

        self._agent_ids.add(agent_id)

    def remove_agent(self, agent_id: str) -> None:
        """Remove an Agent unless it is the current Division manager."""
        if agent_id not in self._agent_ids:
            raise ValueError("Agent is not a member of this Division.")

        if agent_id == self._manager_agent_id:
            raise ValueError("Release the manager relationship before removal.")

        self._agent_ids.remove(agent_id)

    def set_manager(self, agent_id: str | None) -> None:
        """Assign a Division manager who must already be a member."""
        if agent_id is None:
            self._manager_agent_id = None
            return

        self._validate_agent_id(agent_id)

        if agent_id not in self._agent_ids:
            raise ValueError("Division manager must be a Division member.")

        self._manager_agent_id = agent_id

    @staticmethod
    def _validate_agent_id(agent_id: str) -> None:
        """Ensure an Agent reference is a valid UUID version 4."""
        try:
            parsed_id = UUID(agent_id)
        except (ValueError, TypeError, AttributeError):
            raise ValueError("Agent ID must be a valid UUID version 4.") from None

        if parsed_id.version != 4:
            raise ValueError("Agent ID must be a valid UUID version 4.")
