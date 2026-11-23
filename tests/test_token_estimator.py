import unittest
from unittest.mock import patch

from app.utils.token_estimator import estimate_tokens


class TestTokenEstimator(unittest.TestCase):
    """Test approximate token estimation."""

    def test_returns_zero_for_empty_text(self):
        """Verify empty text produces zero estimated tokens."""
        self.assertEqual(estimate_tokens(""), 0)

    def test_estimates_exact_character_ratio(self):
        """Verify text matching the configured ratio is estimated correctly."""
        self.assertEqual(estimate_tokens("abcd"), 1)

    def test_rounds_up_partial_tokens(self):
        """Verify partial token estimates are rounded up."""
        self.assertEqual(estimate_tokens("abcde"), 2)

    def test_rejects_non_string_input(self):
        """Verify non-string input raises a type error."""
        with self.assertRaises(TypeError):
            estimate_tokens(123)

    def test_rejects_zero_character_ratio(self):
        """Verify a zero character ratio raises a value error."""
        with patch("app.utils.token_estimator.CHARS_PER_TOKEN_ESTIMATE", 0):
            with self.assertRaisesRegex(
                ValueError,
                "Character-to-token ratio must be greater than zero.",
            ):
                estimate_tokens("abcd")

    def test_rejects_negative_character_ratio(self):
        """Verify a negative character ratio raises a value error."""
        with patch("app.utils.token_estimator.CHARS_PER_TOKEN_ESTIMATE", -1):
            with self.assertRaisesRegex(
                ValueError,
                "Character-to-token ratio must be greater than zero.",
            ):
                estimate_tokens("abcd")


if __name__ == "__main__":
    unittest.main()
