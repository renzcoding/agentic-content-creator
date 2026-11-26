import unittest

from app.core.agent_message import AgentMessage
from app.core.agent_message_bus import AgentMessageBus


class TestAgentMessageBus(unittest.TestCase):
    """Test in-memory Agent message delivery."""

    def setUp(self):
        """Prepare a message bus and valid Agent identifiers."""
        self.bus = AgentMessageBus()
        self.sender_id = "12345678-1234-4234-8234-123456789012"
        self.receiver_id = "22345678-1234-4234-8234-123456789012"
        self.other_receiver_id = "32345678-1234-4234-8234-123456789012"

    def create_message(self, receiver_id=None):
        """Create a valid test message."""
        return AgentMessage(
            sender_agent_id=self.sender_id,
            receiver_agent_id=receiver_id or self.receiver_id,
            message_type="task_request",
            payload={"task": "Create a content plan"},
        )

    def test_sends_message(self):
        """Verify that a message can be sent."""
        message = self.create_message()

        self.bus.send(message)

        self.assertEqual(self.bus.get_message(message.message_id), message)

    def test_rejects_invalid_message_type(self):
        """Verify that only AgentMessage instances can be sent."""
        with self.assertRaises(TypeError):
            self.bus.send({"message": "invalid"})

    def test_rejects_duplicate_message_id(self):
        """Verify that duplicate message identifiers are rejected."""
        message = self.create_message()
        self.bus.send(message)

        with self.assertRaises(ValueError):
            self.bus.send(message)

    def test_receives_messages_for_target_agent(self):
        """Verify that an Agent receives only its own messages."""
        first_message = self.create_message()
        second_message = self.create_message()
        other_message = self.create_message(self.other_receiver_id)

        self.bus.send(first_message)
        self.bus.send(other_message)
        self.bus.send(second_message)

        received = self.bus.receive(self.receiver_id)

        self.assertEqual(received, [first_message, second_message])

    def test_receive_normalizes_agent_id(self):
        """Verify that uppercase UUID identifiers resolve the same inbox."""
        message = self.create_message()
        self.bus.send(message)

        self.assertEqual(
            self.bus.receive(self.receiver_id.upper()),
            [message],
        )

    def test_receive_rejects_invalid_agent_id(self):
        """Verify that invalid Agent identifiers are rejected."""
        with self.assertRaises(ValueError):
            self.bus.receive("invalid")

    def test_receive_returns_empty_list_for_unknown_inbox(self):
        """Verify that an empty inbox returns an empty list."""
        self.assertEqual(self.bus.receive(self.receiver_id), [])

    def test_receive_preserves_message_history(self):
        """Verify that receiving messages does not delete their history."""
        message = self.create_message()
        self.bus.send(message)

        self.bus.receive(self.receiver_id)

        self.assertEqual(self.bus.list_messages(), [message])

    def test_get_message_returns_none_for_unknown_id(self):
        """Verify that unknown message identifiers return None."""
        self.assertIsNone(
            self.bus.get_message("42345678-1234-4234-8234-123456789012")
        )

    def test_get_message_rejects_invalid_id(self):
        """Verify that invalid message identifiers are rejected."""
        with self.assertRaises(ValueError):
            self.bus.get_message("invalid")

    def test_lists_messages_in_insertion_order(self):
        """Verify that message history preserves insertion order."""
        first_message = self.create_message()
        second_message = self.create_message(self.other_receiver_id)

        self.bus.send(first_message)
        self.bus.send(second_message)

        self.assertEqual(
            self.bus.list_messages(),
            [first_message, second_message],
        )

    def test_returns_empty_message_history(self):
        """Verify that a new bus has no messages."""
        self.assertEqual(self.bus.list_messages(), [])


if __name__ == "__main__":
    unittest.main()
