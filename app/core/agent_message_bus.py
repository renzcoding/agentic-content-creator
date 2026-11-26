from uuid import UUID

from app.core.agent_message import AgentMessage


class AgentMessageBus:
    """Manage in-memory message delivery between Agents."""

    def __init__(self) -> None:
        """Initialize an empty message store."""
        self._messages: dict[str, AgentMessage] = {}

    @staticmethod
    def _normalize_uuid(value: str, field_name: str) -> str:
        """Validate and normalize a UUID v4 identifier."""
        try:
            parsed_id = UUID(value)
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError(f"{field_name} must be a valid UUID v4.") from error

        if parsed_id.version != 4:
            raise ValueError(f"{field_name} must be a valid UUID v4.")

        return str(parsed_id)

    def send(self, message: AgentMessage) -> None:
        """Store a message and reject duplicate message identifiers."""
        if not isinstance(message, AgentMessage):
            raise TypeError("Only AgentMessage instances can be sent.")

        if message.message_id in self._messages:
            raise ValueError(
                f"Message ID '{message.message_id}' already exists."
            )

        self._messages[message.message_id] = message

    def receive(self, agent_id: str) -> list[AgentMessage]:
        """Return messages addressed to an Agent without deleting history."""
        normalized_id = self._normalize_uuid(agent_id, "Agent ID")

        return [
            message
            for message in self._messages.values()
            if message.receiver_agent_id == normalized_id
        ]

    def get_message(self, message_id: str) -> AgentMessage | None:
        """Retrieve a message by its permanent identifier."""
        normalized_id = self._normalize_uuid(message_id, "Message ID")
        return self._messages.get(normalized_id)

    def list_messages(self) -> list[AgentMessage]:
        """Return all stored messages in insertion order."""
        return list(self._messages.values())
