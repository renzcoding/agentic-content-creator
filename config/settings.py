MAX_REVISION_ATTEMPTS = 3
MIN_SCRIPT_LENGTH = 60
OLLAMA_MODEL = "qwen2.5:0.5b"
# Conversation storage configuration.
CONVERSATION_STORAGE_BACKEND = "json"
CONVERSATION_JSON_PATH = "outputs/conversations.json"
CONVERSATION_SQLITE_PATH = "outputs/conversations.db"

# Maximum number of relevance-ranked older messages included in LLM prompts.
RELEVANT_CONTEXT_LIMIT = 5

# Maximum character budgets for conversation and project context in LLM prompts.
RELEVANT_CONTEXT_CHAR_LIMIT = 2000
RECENT_HISTORY_CHAR_LIMIT = 2000
PROJECT_CONTEXT_CHAR_LIMIT = 1000
