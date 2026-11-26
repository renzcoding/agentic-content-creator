import unittest

from app.agents.base_agent import BaseAgent
from app.agents.orchestrator import AgentOrchestrator
from app.core.agent_registry import AgentRegistry


class StubAgent(BaseAgent):
    """Provide a predictable Agent for integration testing."""

    def run(self, task: str) -> str:
        """Return a response for the supplied task."""
        return f"Processed: {task}"


class TestOrchestratorRegistryIntegration(unittest.TestCase):
    """Test Orchestrator integration with AgentRegistry."""

    def setUp(self):
        """Create a registry, orchestrator, and test Agent."""
        self.registry = AgentRegistry()
        self.orchestrator = AgentOrchestrator(registry=self.registry)
        self.agent = StubAgent("Test Agent", "Testing")

    def test_uses_injected_registry(self):
        """Verify that the injected registry is retained."""
        self.assertIs(self.orchestrator.registry, self.registry)

    def test_registers_agent_by_permanent_id(self):
        """Verify that Agent registration is delegated to the registry."""
        self.orchestrator.register_agent(self.agent)

        self.assertIs(
            self.registry.get(self.agent.agent_id),
            self.agent,
        )

    def test_preserves_legacy_agents_lookup(self):
        """Verify that the legacy name-keyed view remains available."""
        self.orchestrator.register_agent(self.agent)

        self.assertIs(
            self.orchestrator.agents["test agent"],
            self.agent,
        )

    def test_rejects_duplicate_agent_names(self):
        """Verify that legacy registration rejects duplicate names."""
        self.orchestrator.register_agent(self.agent)
        duplicate = StubAgent("test agent", "Another role")

        with self.assertRaises(ValueError):
            self.orchestrator.register_agent(duplicate)

    def test_executes_agent_through_registry(self):
        """Verify that task execution resolves the Agent through the registry."""
        self.orchestrator.register_agent(self.agent)

        result = self.orchestrator.execute(
            " TEST AGENT ",
            "Run integration test",
        )

        self.assertEqual(result, "Processed: Run integration test")

    def test_lists_agents_from_registry(self):
        """Verify that the legacy list format remains unchanged."""
        self.orchestrator.register_agent(self.agent)

        self.assertEqual(
            self.orchestrator.list_agents(),
            [{"name": "Test Agent", "role": "Testing"}],
        )


if __name__ == "__main__":
    unittest.main()
