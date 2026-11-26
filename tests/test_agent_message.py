import unittest
from uuid import UUID

from app.core.agent_message import AgentMessage


class TestAgentMessage(unittest.TestCase):
    """Test AgentMessage identity and validation."""

    def setUp(self):
        """Prepare valid message attributes."""
        self.sender_id = str(UUID("12345678-1234-4234-8234-123456789012"))
        self.receiver_id = str(UUID("22345678-1234-4234-8234-123456789012"))

    def test_creates_message_with_generated_id(self):
        """Verify that a message receives a UUID v4 identifier."""
        message = AgentMessage(
            sender_agent_id=self.sender_id,
            receiver_agent_id=self.receiver_id,
            message_type="task_request",
            payload={"task": "Create a content plan"},
        )

        parsed_id = UUID(message.message_id)

        self.assertEqual(parsed_id.version, 4)

    def test_preserves_message_attributes(self):
        """Verify that all supplied message attributes are preserved."""
        payload = {"task": "Create a content plan"}

        message = AgentMessage(
            sender_agent_id=self.sender_id,
            receiver_agent_id=self.receiver_id,
            message_type="task_request",
            payload=payload,
        )

        self.assertEqual(message.sender_agent_id, self.sender_id)
        self.assertEqual(message.receiver_agent_id, self.receiver_id)
        self.assertEqual(message.message_type, "task_request")
        self.assertEqual(message.payload, payload)
        self.assertIsNotNone(message.timestamp)

    def test_accepts_existing_message_id(self):
        """Verify that a valid UUID v4 message ID can be restored."""
        message_id = str(UUID("32345678-1234-4234-8234-123456789012"))

        message = AgentMessage(
            sender_agent_id=self.sender_id,
            receiver_agent_id=self.receiver_id,
            message_type="task_result",
            payload={"result": "Completed"},
            message_id=message_id,
        )

        self.assertEqual(message.message_id, message_id)

    def test_rejects_invalid_sender_id(self):
        """Verify that invalid sender identifiers are rejected."""
        with self.assertRaises(ValueError):
            AgentMessage(
                sender_agent_id="invalid",
                receiver_agent_id=self.receiver_id,
                message_type="task_request",
                payload={},
            )

    def test_rejects_invalid_receiver_id(self):
        """Verify that invalid receiver identifiers are rejected."""
        with self.assertRaises(ValueError):
            AgentMessage(
                sender_agent_id=self.sender_id,
                receiver_agent_id="invalid",
                message_type="task_request",
                payload={},
            )

    def test_rejects_non_v4_agent_ids(self):
        """Verify that Agent identifiers must use UUID v4."""
        with self.assertRaises(ValueError):
            AgentMessage(
                sender_agent_id="12345678-1234-1234-8234-123456789012",
                receiver_agent_id=self.receiver_id,
                message_type="task_request",
                payload={},
            )

    def test_rejects_empty_message_type(self):
        """Verify that message types cannot be empty."""
        with self.assertRaises(ValueError):
            AgentMessage(
                sender_agent_id=self.sender_id,
                receiver_agent_id=self.receiver_id,
                message_type=" ",
                payload={},
            )

    def test_rejects_invalid_message_id(self):
        """Verify that invalid message identifiers are rejected."""
        with self.assertRaises(ValueError):
            AgentMessage(
                sender_agent_id=self.sender_id,
                receiver_agent_id=self.receiver_id,
                message_type="task_request",
                payload={},
                message_id="invalid",
            )

    def test_message_id_is_read_only(self):
        """Verify that message identity cannot be reassigned."""
        message = AgentMessage(
            sender_agent_id=self.sender_id,
            receiver_agent_id=self.receiver_id,
            message_type="task_request",
            payload={},
        )

        with self.assertRaises(AttributeError):
            message.message_id = self.sender_id


if __name__ == "__main__":
    unittest.main()
