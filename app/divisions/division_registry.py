from app.divisions.base_division import BaseDivision


class DivisionRegistry:
    """Own Division registration, lookup, and Agent reference validation."""

    def __init__(self) -> None:
        """Initialize an empty Division registry."""
        self._divisions: dict[str, BaseDivision] = {}

    def register(self, division: BaseDivision) -> None:
        """Register a Division and reject duplicate identifiers."""
        if not isinstance(division, BaseDivision):
            raise TypeError("Expected a BaseDivision instance.")

        if division.division_id in self._divisions:
            raise ValueError("Division ID is already registered.")

        self._divisions[division.division_id] = division

    @staticmethod
    def _validate_division_id(division_id: str) -> str:
        """Validate and normalize a Division identifier."""
        if not isinstance(division_id, str):
            raise TypeError("Division ID must be a string.")

        normalized_id = division_id.strip()
        if not normalized_id:
            raise ValueError("Division ID must not be empty.")

        return normalized_id

    def get(self, division_id: str) -> BaseDivision | None:
        """Retrieve a Division by its stable identifier."""
        normalized_id = self._validate_division_id(division_id)
        return self._divisions.get(normalized_id)

    def list_divisions(self) -> list[BaseDivision]:
        """Return registered Divisions in registration order."""
        return list(self._divisions.values())

    def validate_agent_references(self, agent_ids: set[str]) -> None:
        """Ensure all Division members and managers reference known Agents."""
        if not isinstance(agent_ids, set):
            raise TypeError("Agent IDs must be provided as a set.")

        if any(not isinstance(agent_id, str) for agent_id in agent_ids):
            raise TypeError("Agent IDs must contain only strings.")

        if any(not agent_id.strip() for agent_id in agent_ids):
            raise ValueError("Agent IDs must not contain empty strings.")

        for division in self._divisions.values():
            for agent_id in division.agent_ids:
                if agent_id not in agent_ids:
                    raise ValueError(
                        f"Division '{division.division_id}' references "
                        f"unknown Agent '{agent_id}'."
                    )

            manager_agent_id = division.manager_agent_id
            if (
                manager_agent_id is not None
                and manager_agent_id not in agent_ids
            ):
                raise ValueError(
                    f"Division '{division.division_id}' references "
                    f"unknown manager Agent '{manager_agent_id}'."
                )
