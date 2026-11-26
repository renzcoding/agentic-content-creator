import unittest

from app.agents.base_agent import BaseAgent
from app.core.agent_message import AgentMessage
from app.core.agent_message_bus import AgentMessageBus
from app.core.agent_registry import AgentRegistry
from app.divisions.base_division import BaseDivision
from app.divisions.division_registry import DivisionRegistry


class StubAgent(BaseAgent):
    """Provide a predictable Agent for core integration testing."""

    def run(self, task: str) -> str:
        """Return a predictable response for the supplied task."""
        return f"Processed: {task}"


class TestCoreFoundationIntegration(unittest.TestCase):
    """Test interactions between core foundation components."""

    def setUp(self):
        """Initialize registries and two real Agent instances."""
        self.agent_registry = AgentRegistry()
        self.division_registry = DivisionRegistry()
        self.message_bus = AgentMessageBus()

        self.sender = StubAgent("Sender Agent", "Message Sender")
        self.receiver = StubAgent("Receiver Agent", "Message Receiver")

    def test_agent_registry_and_division_registry_integration(self):
        """Verify Division references against registered Agent identities."""
        self.agent_registry.register(self.sender)
        self.agent_registry.register(self.receiver)

        division = BaseDivision(
            division_id="engineering_technology",
            name="Engineering & Technology",
        )
        division.assign_agent(self.sender.agent_id)
        division.assign_agent(self.receiver.agent_id)
        division.set_manager(self.sender.agent_id)

        self.division_registry.register(division)

        registered_agent_ids = {
            agent.agent_id
            for agent in self.agent_registry.list_agents()
        }

        self.division_registry.validate_agent_references(
            registered_agent_ids
        )

        self.assertIs(
            self.division_registry.get("engineering_technology"),
            division,
        )

    def test_division_registry_detects_unregistered_agent(self):
        """Verify stale Division references are detected after unregistration."""
        self.agent_registry.register(self.sender)

        division = BaseDivision(
            division_id="content_development",
            name="Content Development",
        )
        division.assign_agent(self.sender.agent_id)
        self.division_registry.register(division)

        self.agent_registry.unregister(self.sender.agent_id)

        registered_agent_ids = {
            agent.agent_id
            for agent in self.agent_registry.list_agents()
        }

        with self.assertRaises(ValueError):
            self.division_registry.validate_agent_references(
                registered_agent_ids
            )

    def test_registered_agents_exchange_messages_through_message_bus(self):
        """Verify messages can be routed using registered Agent identities."""
        self.agent_registry.register(self.sender)
        self.agent_registry.register(self.receiver)

        message = AgentMessage(
            sender_agent_id=self.sender.agent_id,
            receiver_agent_id=self.receiver.agent_id,
            message_type="task_request",
            payload={"task": "Create a content plan"},
        )

        self.message_bus.send(message)

        received_messages = self.message_bus.receive(
            self.receiver.agent_id
        )

        self.assertEqual(received_messages, [message])
        self.assertEqual(
            self.message_bus.receive(self.sender.agent_id),
            [],
        )
        self.assertIs(
            self.agent_registry.get(message.sender_agent_id),
            self.sender,
        )
        self.assertIs(
            self.agent_registry.get(message.receiver_agent_id),
            self.receiver,
        )


if __name__ == "__main__":
    unittest.main()
