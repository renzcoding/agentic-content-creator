class ConversationDataValidator:
    """Validate conversation session data before persistence."""

    @staticmethod
    def validate(sessions: dict) -> None:
        """Reject invalid session structures and message fields."""
        if not isinstance(sessions, dict):
            raise ValueError("Conversation sessions must be a dictionary.")

        for session_id, messages in sessions.items():
            if not isinstance(session_id, str) or not session_id.strip():
                raise ValueError("Session ID must be a non-empty string.")

            if not isinstance(messages, list):
                raise ValueError("Session messages must be a list.")

            for message in messages:
                if not isinstance(message, dict):
                    raise ValueError("Each conversation message must be a dictionary.")

                role = message.get("role")
                content = message.get("content")

                if not isinstance(role, str) or not role.strip():
                    raise ValueError("Message role must be a non-empty string.")

                if not isinstance(content, str) or not content.strip():
                    raise ValueError("Message content must be a non-empty string.")
