import unittest
import tempfile
from pathlib import Path
from unittest.mock import Mock

from app.agents.product_manager import ProductManagerAgent
from app.memory.base_memory import BaseMemory
from app.memory.conversation_memory import ConversationMemory
from app.services.llm.base_provider import BaseLLMProvider


class TestProductManagerAgent(unittest.TestCase):
    """Test product manager behavior with injected dependencies."""

    def setUp(self):
        """Create mock dependencies and initialize the agent."""
        self.provider = Mock(spec=BaseLLMProvider)
        self.provider.generate.return_value = (
            "PRODUCT REQUIREMENTS\n"
            "Objective: Create a content planning dashboard\n"
            "Acceptance Criteria: Users can plan content."
        )
        self.memory = Mock(spec=BaseMemory)
        self.agent = ProductManagerAgent(
            provider=self.provider,
            memory=self.memory,
        )

    def test_generates_product_requirements(self):
        """Verify that the agent returns provider-generated requirements."""
        result = self.agent.run("Create a content planning dashboard")

        self.assertIn("PRODUCT REQUIREMENTS", result)
        self.assertIn("content planning dashboard", result)
        self.assertIn("Acceptance Criteria", result)
        self.provider.generate.assert_called_once()

    def test_rejects_empty_task(self):
        """Verify that empty tasks are rejected without calling the provider."""
        with self.assertRaises(ValueError):
            self.agent.run("   ")

        self.provider.generate.assert_not_called()

    def test_includes_remembered_context_in_prompt(self):
        """Verify that stored project context is included in the LLM prompt."""
        self.memory.retrieve.return_value = "Use React and Laravel."

        self.agent.run("Build a dashboard")

        prompt = self.provider.generate.call_args.args[0]
        self.assertIn("Previous Context: Use React and Laravel.", prompt)
        self.memory.retrieve.assert_called_once_with(
            "Product Manager:project_context"
        )

    def test_runs_without_memory_context(self):
        """Verify that missing context does not affect requirement generation."""
        self.memory.retrieve.return_value = None

        result = self.agent.run("Build a dashboard")

        prompt = self.provider.generate.call_args.args[0]
        self.assertNotIn("Previous Context:", prompt)
        self.assertIn("PRODUCT REQUIREMENTS", result)

    def test_runs_without_memory_configuration(self):
        """Verify that the agent works when memory is not configured."""
        agent = ProductManagerAgent(provider=self.provider)

        result = agent.run("Build a dashboard")

        self.assertIn("PRODUCT REQUIREMENTS", result)
        self.provider.generate.assert_called_once()


    def test_includes_recent_conversation_in_prompt(self):
        """Verify that recent conversation is included in the LLM prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation = ConversationMemory(
                str(Path(temp_dir) / "conversations.json")
            )
            conversation.add_message("user", "Build a content platform.")
            conversation.add_message("assistant", "Use React and Laravel.")

            agent = ProductManagerAgent(
                provider=self.provider,
                conversation_memory=conversation,
            )
            agent.run("Add an analytics feature")

            prompt = self.provider.generate.call_args.args[0]
            self.assertIn("Recent Conversation:", prompt)
            self.assertIn("Build a content platform.", prompt)
            self.assertIn("Use React and Laravel.", prompt)

    def test_persists_user_and_assistant_messages(self):
        """Verify that successful responses are saved to conversation history."""
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation = ConversationMemory(
                str(Path(temp_dir) / "conversations.json")
            )
            agent = ProductManagerAgent(
                provider=self.provider,
                conversation_memory=conversation,
            )

            result = agent.run("Build a dashboard")
            history = conversation.get_history()

            self.assertEqual(len(history), 2)
            self.assertEqual(history[0]["role"], "user")
            self.assertEqual(history[0]["content"], "Build a dashboard")
            self.assertEqual(history[1]["role"], "assistant")
            self.assertEqual(history[1]["content"], result)

    def test_limits_recent_conversation_history(self):
        """Verify that only the configured number of messages enter the prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation = ConversationMemory(
                str(Path(temp_dir) / "conversations.json")
            )
            conversation.add_message("user", "Old message")
            conversation.add_message("assistant", "Old response")
            conversation.add_message("user", "Recent message")

            agent = ProductManagerAgent(
                provider=self.provider,
                conversation_memory=conversation,
                history_limit=2,
            )
            agent.run("Continue the project")

            prompt = self.provider.generate.call_args.args[0]
            self.assertNotIn("Old message", prompt)
            self.assertIn("Old response", prompt)
            self.assertIn("Recent message", prompt)


    def test_isolates_agent_conversation_sessions(self):
        """Verify that the agent reads and writes only its assigned session."""
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation = ConversationMemory(
                str(Path(temp_dir) / "conversations.json")
            )
            conversation.add_message("user", "Private session A", "session-a")

            agent = ProductManagerAgent(
                provider=self.provider,
                conversation_memory=conversation,
                session_id="session-b",
            )
            agent.run("Build a dashboard")

            prompt = self.provider.generate.call_args.args[0]
            self.assertNotIn("Private session A", prompt)

            history_a = conversation.get_history(session_id="session-a")
            history_b = conversation.get_history(session_id="session-b")

            self.assertEqual(len(history_a), 1)
            self.assertEqual(len(history_b), 2)

    def test_rejects_empty_session_id(self):
        """Verify that the agent rejects an empty session identifier."""
        with self.assertRaises(ValueError):
            ProductManagerAgent(
                provider=self.provider,
                session_id=" ",
            )

    def test_includes_relevant_older_messages_in_prompt(self):
        """Verify that older keyword-matching messages enter the prompt."""
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation = ConversationMemory(
                str(Path(temp_dir) / "conversations.json")
            )
            conversation.add_message(
                "user", "We chose React for the frontend."
            )
            conversation.add_message(
                "assistant", "The backend uses Laravel."
            )
            conversation.add_message(
                "user", "The dashboard needs analytics."
            )
            conversation.add_message(
                "assistant", "Use charts for reporting."
            )

            agent = ProductManagerAgent(
                provider=self.provider,
                conversation_memory=conversation,
                history_limit=2,
            )
            agent.run("Continue the React frontend development")

            prompt = self.provider.generate.call_args.args[0]
            self.assertIn("React for the frontend", prompt)


    def test_searches_relevant_messages_with_multiple_keywords(self):
        """Verify that relevant messages are searched with one keyword list."""
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation = ConversationMemory(
                str(Path(temp_dir) / "conversations.json")
            )
            conversation.add_message(
                "user", "React frontend development is important."
            )
            conversation.add_message(
                "assistant", "Use reusable React components."
            )
            conversation.add_message(
                "user", "The database uses PostgreSQL."
            )

            agent = ProductManagerAgent(
                provider=self.provider,
                conversation_memory=conversation,
                history_limit=1,
            )

            original_search = conversation.search_messages
            search_calls = []

            def track_search(keyword, session_id="default", limit=None):
                search_calls.append(keyword)
                return original_search(keyword, session_id, limit)

            conversation.search_messages = Mock(side_effect=track_search)

            agent.run("Continue React frontend development")

            self.assertEqual(len(search_calls), 1)
            self.assertIsInstance(search_calls[0], list)
            self.assertEqual(
                set(search_calls[0]),
                {"continue", "react", "frontend", "development"},
            )


    def test_prioritizes_more_relevant_messages_in_prompt(self):
        """Verify that higher-ranked messages appear first in relevant context."""
        with tempfile.TemporaryDirectory() as temp_dir:
            conversation = ConversationMemory(
                str(Path(temp_dir) / "conversations.json")
            )
            conversation.add_message("user", "React is useful.")
            conversation.add_message(
                "assistant", "React frontend development uses reusable components."
            )
            conversation.add_message(
                "user", "React frontend development improves the dashboard."
            )
            conversation.add_message(
                "assistant", "Frontend tools are important."
            )

            agent = ProductManagerAgent(
                provider=self.provider,
                conversation_memory=conversation,
                history_limit=1,
            )
            agent.run("Explain React frontend development")

            prompt = self.provider.generate.call_args.args[0]
            relevant_section = prompt.split(
                "Relevant Previous Conversation:\n", 1
            )[1].split("\n\nObjective:", 1)[0]

            self.assertLess(
                relevant_section.index("React frontend development uses"),
                relevant_section.index("React is useful."),
            )


if __name__ == "__main__":
    unittest.main()
