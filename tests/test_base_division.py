import unittest
import uuid

from app.divisions.base_division import BaseDivision


def create_agent_id():
    """Generate a valid UUID v4 Agent identifier for testing."""
    return str(uuid.uuid4())


class TestBaseDivision(unittest.TestCase):
    """Test Division identity, membership, and manager relationships."""

    def setUp(self):
        """Create a Division with stable organizational identity."""
        self.division = BaseDivision(
            division_id="engineering_technology",
            name="Engineering & Technology",
            description="Build and maintain software systems.",
        )
        self.agent_id = create_agent_id()

    def test_initializes_division_metadata(self):
        self.assertEqual(
            self.division.division_id,
            "engineering_technology",
        )
        self.assertEqual(
            self.division.name,
            "Engineering & Technology",
        )
        self.assertEqual(
            self.division.description,
            "Build and maintain software systems.",
        )

    def test_division_id_is_read_only(self):
        """Verify the stable Division identifier cannot be reassigned."""
        with self.assertRaises(AttributeError):
            self.division.division_id = "content_development"

    def test_rejects_invalid_division_id(self):
        with self.assertRaises(ValueError):
            BaseDivision("Engineering Team", "Engineering")

    def test_rejects_empty_division_name(self):
        with self.assertRaises(ValueError):
            BaseDivision("engineering", " ")

    def test_assigns_agent_membership(self):
        self.division.assign_agent(self.agent_id)

        self.assertTrue(self.division.has_agent(self.agent_id))
        self.assertIn(self.agent_id, self.division.agent_ids)

    def test_rejects_duplicate_agent_membership(self):
        self.division.assign_agent(self.agent_id)

        with self.assertRaises(ValueError):
            self.division.assign_agent(self.agent_id)

    def test_rejects_invalid_agent_identifier(self):
        with self.assertRaises(ValueError):
            self.division.assign_agent("invalid-agent-id")

    def test_removes_agent_membership(self):
        self.division.assign_agent(self.agent_id)
        self.division.remove_agent(self.agent_id)

        self.assertFalse(self.division.has_agent(self.agent_id))

    def test_rejects_removing_nonmember(self):
        with self.assertRaises(ValueError):
            self.division.remove_agent(self.agent_id)

    def test_assigns_manager_from_existing_member(self):
        self.division.assign_agent(self.agent_id)
        self.division.set_manager(self.agent_id)

        self.assertEqual(
            self.division.manager_agent_id,
            self.agent_id,
        )

    def test_rejects_manager_who_is_not_a_member(self):
        with self.assertRaises(ValueError):
            self.division.set_manager(self.agent_id)

    def test_releases_manager_relationship(self):
        self.division.assign_agent(self.agent_id)
        self.division.set_manager(self.agent_id)
        self.division.set_manager(None)

        self.assertIsNone(self.division.manager_agent_id)

    def test_prevents_removing_current_manager(self):
        self.division.assign_agent(self.agent_id)
        self.division.set_manager(self.agent_id)

        with self.assertRaises(ValueError):
            self.division.remove_agent(self.agent_id)


if __name__ == "__main__":
    unittest.main()
