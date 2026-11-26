from datetime import datetime, timezone
from uuid import UUID, uuid4


class AgentMessage:
    """Represent a validated message exchanged between Agents."""

    def __init__(
        self,
        sender_agent_id: str,
        receiver_agent_id: str,
        message_type: str,
        payload: dict,
        message_id: str | None = None,
        timestamp: datetime | None = None,
    ) -> None:
        """Initialize and validate an immutable Agent message."""
        self._message_id = self._validate_uuid(message_id or str(uuid4()), "Message ID")
        self._sender_agent_id = self._validate_uuid(sender_agent_id, "Sender Agent ID")
        self._receiver_agent_id = self._validate_uuid(receiver_agent_id, "Receiver Agent ID")

        if not isinstance(message_type, str) or not message_type.strip():
            raise ValueError("Message type must not be empty.")

        if not isinstance(payload, dict):
            raise TypeError("Message payload must be a dictionary.")

        if timestamp is not None and not isinstance(timestamp, datetime):
            raise TypeError("Message timestamp must be a datetime.")

        self._message_type = message_type.strip()
        self._payload = payload.copy()
        self._timestamp = timestamp or datetime.now(timezone.utc)

    @staticmethod
    def _validate_uuid(value: str, field_name: str) -> str:
        """Validate and normalize a UUID v4 identifier."""
        try:
            parsed_id = UUID(value)
        except (ValueError, TypeError, AttributeError) as error:
            raise ValueError(f"{field_name} must be a valid UUID v4.") from error

        if parsed_id.version != 4:
            raise ValueError(f"{field_name} must be a valid UUID v4.")

        return str(parsed_id)

    @property
    def message_id(self) -> str:
        """Return the permanent message identifier."""
        return self._message_id

    @property
    def sender_agent_id(self) -> str:
        """Return the sender Agent identifier."""
        return self._sender_agent_id

    @property
    def receiver_agent_id(self) -> str:
        """Return the receiver Agent identifier."""
        return self._receiver_agent_id

    @property
    def message_type(self) -> str:
        """Return the message type."""
        return self._message_type

    @property
    def payload(self) -> dict:
        """Return a copy of the message payload."""
        return self._payload.copy()

    @property
    def timestamp(self) -> datetime:
        """Return the message creation timestamp."""
        return self._timestamp
