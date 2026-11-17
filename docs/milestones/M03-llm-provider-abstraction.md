# M03 - LLM Provider Abstraction

**Date:** November 17, 2026
**Status:** Completed
**Test Result:** 37 tests passed

## 1. Objective

Build an abstraction layer that allows AI agents to use different
Large Language Model (LLM) providers without depending directly
on a specific provider implementation.

The initial implementation uses Ollama as the local LLM provider.

## 2. Architecture

The architecture separates agent responsibilities from LLM provider
implementations.

```text
ProductManagerAgent
        |
        v
  BaseLLMProvider
        |
        v
   OllamaProvider
        |
        v
  Ollama Service
        |
        v
  Local Ollama API
Main Components
Component	Responsibility
BaseLLMProvider	Defines the standard provider interface.
OllamaProvider	Implements the interface for Ollama.
Ollama Service	Handles HTTP communication with Ollama.
ProductManagerAgent	Uses an injected provider to generate requirements.

3. Base LLM Provider
File: app/services/llm/base_provider.py
from abc import ABC, abstractmethodclass BaseLLMProvider(ABC):    """Define the standard interface for all LLM providers."""    @abstractmethod    def generate(self, prompt: str) -> str:        """Generate text from a prompt using an LLM provider."""        raise NotImplementedError



Explanation
- ABC enables the creation of abstract base classes.
- abstractmethod requires subclasses to implement generate().
- generate(prompt) defines the common method for text generation.
- raise NotImplementedError marks the method as requiring an implementation.
Agents can depend on this interface instead of a specific LLM service.
4. Ollama Provider
File: app/services/llm/ollama_provider.py
from app.services.llm.base_provider import BaseLLMProviderfrom app.services.ollama_service import generate_responseclass OllamaProvider(BaseLLMProvider):    """Provide local LLM generation through Ollama."""    def generate(self, prompt: str) -> str:        """Generate text using the configured local Ollama model."""        return generate_response(prompt)



Explanation
- OllamaProvider inherits from BaseLLMProvider.
- generate() implements the required provider interface.
- generate_response() delegates HTTP communication to the Ollama service.
- The provider acts as an adapter between agents and Ollama.
5. Dependency Injection
File: app/agents/product_manager.py

The Product Manager Agent receives its LLM provider through its constructor.

Important implementation concepts:
- provider is an optional dependency.
- BaseLLMProvider is the abstraction used by the agent.
- OllamaProvider is the default implementation.
- self.provider.generate(prompt) delegates generation to the selected provider.
The provider initialization is:
self.provider = provider if provider is not None else OllamaProvider()



This approach is called dependency injection.

It allows the provider implementation to be replaced without rewriting
the agent's business logic. It also allows tests to inject mock providers
without making real API requests.
6. Configuration
File: config/settings.py

Current configuration:
MAX_REVISION_ATTEMPTS = 3MIN_SCRIPT_LENGTH = 60OLLAMA_MODEL = "qwen2.5:0.5b"



The model is configured centrally so it can be changed without modifying
the provider or agent implementation.
7. Testing Strategy
The provider and agent are tested independently using Python's
standard-library unittest framework.
Product Manager Tests
File: tests/test_product_manager.py

The tests use unittest.mock.Mock to simulate an LLM provider.

Covered scenarios:
- The agent returns provider-generated requirements.
- Empty tasks raise ValueError.
- The provider is not called when the task is empty.
Ollama Provider Tests
File: tests/test_ollama_provider.py

The generate_response() function is mocked to verify that:
- The prompt is forwarded to the Ollama service.
- The generated response is returned correctly.
Ollama Service Tests
File: tests/test_ollama_service.py

Covered scenarios:
- Empty prompts are rejected.
- Generated responses are extracted and trimmed.
- Connection errors are converted into readable runtime errors.
Full Test Suite
Command:
python -m unittest discover -s tests -v


Latest recorded result:
Ran 37 tests in 0.071s

OK


All 37 tests passed during the latest full test run.
8. Benefits
1. Provider independence: Agents do not depend directly on Ollama.
2. Testability: Providers can be mocked during unit testing.
3. Maintainability: Provider communication is separated from agent logic.
4. Extensibility: Additional providers can implement the same interface.
5. Local-first development: Ollama enables local inference without a paid API.
9. Future Extensions
Potential future provider implementations include:
- OpenAI-compatible APIs
- Google Gemini
- Groq
- OpenRouter
- Other local inference engines
Each provider should implement BaseLLMProvider without requiring
changes to the agent interface.
10. Milestone Completion Criteria
- [x] Create the base LLM provider interface.
- [x] Implement the Ollama provider.
- [x] Integrate provider dependency injection into ProductManagerAgent.
- [x] Add provider unit tests.
- [x] Add Product Manager unit tests.
- [x] Run the complete test suite successfully.
Milestone M03: Completed.
