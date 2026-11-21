import unittest

from app.memory.conversation_data_validator import ConversationDataValidator


class TestConversationDataValidator(unittest.TestCase):
    """Test conversation data validation rules."""

    def test_accepts_valid_sessions(self):
        """Verify valid conversation sessions are accepted."""
        sessions = {
            "default": [
                {"role": "user", "content": "Hello"},
                {"role": "assistant", "content": "Hi"},
            ]
        }

        self.assertIsNone(ConversationDataValidator.validate(sessions))

    def test_rejects_non_dictionary_sessions(self):
        """Verify session data must be a dictionary."""
        with self.assertRaises(ValueError):
            ConversationDataValidator.validate([])

    def test_rejects_empty_session_id(self):
        """Verify session identifiers cannot be empty."""
        with self.assertRaises(ValueError):
            ConversationDataValidator.validate({" ": []})

    def test_rejects_non_list_messages(self):
        """Verify session messages must be stored in a list."""
        with self.assertRaises(ValueError):
            ConversationDataValidator.validate({"default": "invalid"})

    def test_rejects_non_dictionary_message(self):
        """Verify each message must be a dictionary."""
        with self.assertRaises(ValueError):
            ConversationDataValidator.validate({"default": ["invalid"]})

    def test_rejects_empty_role(self):
        """Verify message roles cannot be empty."""
        with self.assertRaises(ValueError):
            ConversationDataValidator.validate({
                "default": [{"role": " ", "content": "Hello"}]
            })

    def test_rejects_empty_content(self):
        """Verify message content cannot be empty."""
        with self.assertRaises(ValueError):
            ConversationDataValidator.validate({
                "default": [{"role": "user", "content": " "}]
            })

    def test_rejects_non_string_message_fields(self):
        """Verify role and content must be strings."""
        with self.assertRaises(ValueError):
            ConversationDataValidator.validate({
                "default": [{"role": "user", "content": None}]
            })


if __name__ == "__main__":
    unittest.main()
