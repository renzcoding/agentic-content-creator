import unittest
import uuid

from app.divisions.base_division import BaseDivision
from app.divisions.division_registry import DivisionRegistry


def create_agent_id():
    """Generate a valid UUID v4 Agent identifier for testing."""
    return str(uuid.uuid4())


class TestDivisionRegistry(unittest.TestCase):
    """Test Division registration, lookup, and reference validation."""

    def setUp(self):
        """Create a registry and two unique Divisions."""
        self.registry = DivisionRegistry()
        self.division = BaseDivision(
            division_id="engineering_technology",
            name="Engineering & Technology",
        )
        self.second_division = BaseDivision(
            division_id="content_development",
            name="Content Development",
        )

    def test_registers_and_retrieves_division(self):
        self.registry.register(self.division)

        result = self.registry.get("engineering_technology")

        self.assertIs(result, self.division)

    def test_rejects_duplicate_division_id(self):
        self.registry.register(self.division)

        duplicate = BaseDivision(
            division_id="engineering_technology",
            name="Duplicate Engineering",
        )

        with self.assertRaises(ValueError):
            self.registry.register(duplicate)

    def test_returns_none_for_unknown_division(self):
        self.assertIsNone(self.registry.get("unknown_division"))

    def test_lists_registered_divisions(self):
        self.registry.register(self.division)
        self.registry.register(self.second_division)

        result = self.registry.list_divisions()

        self.assertEqual(
            result,
            [self.division, self.second_division],
        )

    def test_validates_agent_membership_references(self):
        agent_id = create_agent_id()
        self.division.assign_agent(agent_id)
        self.division.set_manager(agent_id)
        self.registry.register(self.division)

        self.registry.validate_agent_references({agent_id})

    def test_rejects_unknown_agent_membership_reference(self):
        agent_id = create_agent_id()
        self.division.assign_agent(agent_id)
        self.registry.register(self.division)

        with self.assertRaises(ValueError):
            self.registry.validate_agent_references(set())

    def test_rejects_unknown_manager_reference(self):
        agent_id = create_agent_id()
        self.division.assign_agent(agent_id)
        self.division.set_manager(agent_id)
        self.registry.register(self.division)

        with self.assertRaises(ValueError):
            self.registry.validate_agent_references(set())


if __name__ == "__main__":
    unittest.main()
