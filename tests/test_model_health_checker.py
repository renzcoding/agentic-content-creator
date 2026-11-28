import unittest
from unittest.mock import Mock

from app.services.llm.model_configuration import ModelConfiguration
from app.services.llm.model_health_checker import ModelHealthChecker


class TestModelHealthChecker(unittest.TestCase):
    """Test model health checks using injected callbacks."""

    def setUp(self) -> None:
        """Initialize a sample model configuration."""
        self.configuration = ModelConfiguration(
            model_id="local-model",
            provider_id="ollama",
            model_name="qwen2.5:0.5b",
            is_local=True,
        )

    def test_returns_true_for_healthy_model(self) -> None:
        """Verify healthy models return True."""
        callback = Mock(return_value=True)
        checker = ModelHealthChecker(callback)

        self.assertTrue(checker.check(self.configuration))
        callback.assert_called_once_with(self.configuration)

    def test_returns_false_for_unhealthy_model(self) -> None:
        """Verify unhealthy models return False."""
        checker = ModelHealthChecker(Mock(return_value=False))

        self.assertFalse(checker.check(self.configuration))

    def test_returns_false_when_callback_raises(self) -> None:
        """Verify callback failures are treated as unhealthy."""
        callback = Mock(side_effect=RuntimeError("Provider unavailable"))
        checker = ModelHealthChecker(callback)

        self.assertFalse(checker.check(self.configuration))

    def test_skips_disabled_model(self) -> None:
        """Verify disabled models are not checked."""
        disabled_configuration = ModelConfiguration(
            model_id="disabled-model",
            provider_id="ollama",
            model_name="disabled-model",
            enabled=False,
            is_local=True,
        )
        callback = Mock(return_value=True)
        checker = ModelHealthChecker(callback)

        self.assertFalse(checker.check(disabled_configuration))
        callback.assert_not_called()

    def test_rejects_invalid_callback(self) -> None:
        """Verify the callback must be callable."""
        with self.assertRaises(TypeError):
            ModelHealthChecker("invalid")

    def test_rejects_invalid_configuration(self) -> None:
        """Verify the checker requires a model configuration."""
        checker = ModelHealthChecker(Mock(return_value=True))

        with self.assertRaises(TypeError):
            checker.check("invalid")

    def test_rejects_non_boolean_callback_result(self) -> None:
        """Verify callback results must be boolean values."""
        checker = ModelHealthChecker(Mock(return_value="healthy"))

        with self.assertRaises(TypeError):
            checker.check(self.configuration)


if __name__ == "__main__":
    unittest.main()
