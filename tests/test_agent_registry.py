import unittest
from uuid import uuid4

from app.agents.base_agent import BaseAgent
from app.core.agent_registry import AgentRegistry


class StubAgent(BaseAgent):
    """Provide a lightweight Agent for registry testing."""

    def run(self, task: str) -> str:
        """Return a predictable response for the supplied task."""
        return f"Processed: {task}"


class TestAgentRegistry(unittest.TestCase):
    """Test Agent registration, lookup, and lifecycle management."""

    def setUp(self):
        """Create a fresh registry and test Agents."""
        self.registry = AgentRegistry()
        self.agent = StubAgent("Test Agent", "Testing")
        self.second_agent = StubAgent("Second Agent", "Testing")

    def test_registers_agent_by_permanent_id(self):
        """Verify that an Agent can be registered using its permanent ID."""
        self.registry.register(self.agent)

        self.assertIs(self.registry.get(self.agent.agent_id), self.agent)

    def test_rejects_duplicate_agent_id(self):
        """Verify that duplicate permanent IDs are rejected."""
        duplicate = StubAgent(
            "Another Agent",
            "Testing",
            agent_id=self.agent.agent_id,
        )
        self.registry.register(self.agent)

        with self.assertRaises(ValueError):
            self.registry.register(duplicate)

    def test_rejects_non_agent_registration(self):
        """Verify that objects outside the BaseAgent contract are rejected."""
        with self.assertRaises(TypeError):
            self.registry.register(object())

    def test_returns_none_for_unknown_agent_id(self):
        """Verify that unknown Agent IDs return None."""
        self.assertIsNone(self.registry.get(str(uuid4())))

    def test_unregisters_agent_by_id(self):
        """Verify that an Agent can be explicitly unregistered."""
        self.registry.register(self.agent)

        removed = self.registry.unregister(self.agent.agent_id)

        self.assertIs(removed, self.agent)
        self.assertIsNone(self.registry.get(self.agent.agent_id))

    def test_returns_none_when_unregistering_unknown_id(self):
        """Verify that unregistering an unknown ID returns None."""
        self.assertIsNone(self.registry.unregister(str(uuid4())))

    def test_lists_registered_agents(self):
        """Verify that all registered Agents are returned in insertion order."""
        self.registry.register(self.agent)
        self.registry.register(self.second_agent)

        self.assertEqual(
            self.registry.list_agents(),
            [self.agent, self.second_agent],
        )

    def test_returns_empty_list_when_no_agents_are_registered(self):
        """Verify that an empty registry returns an empty list."""
        self.assertEqual(self.registry.list_agents(), [])

    def test_finds_agent_by_name_case_insensitively(self):
        """Verify that secondary name lookup ignores letter casing."""
        self.registry.register(self.agent)

        self.assertIs(
            self.registry.get_by_name("  TEST AGENT  "),
            self.agent,
        )

    def test_returns_none_for_unknown_agent_name(self):
        """Verify that unknown Agent names return None."""
        self.assertIsNone(self.registry.get_by_name("Unknown Agent"))

    def test_rejects_ambiguous_agent_name_lookup(self):
        """Verify that duplicate names cannot produce arbitrary lookup results."""
        first = StubAgent("Shared Name", "First Role")
        second = StubAgent("Shared Name", "Second Role")
        self.registry.register(first)
        self.registry.register(second)

        with self.assertRaises(ValueError):
            self.registry.get_by_name("Shared Name")


if __name__ == "__main__":
    unittest.main()
