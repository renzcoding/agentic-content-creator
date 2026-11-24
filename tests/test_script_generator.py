import unittest

from app.tools.script_generator import (
    build_generation_prompt,
    build_revision_prompt,
)


class TestScriptGeneratorPrompts(unittest.TestCase):
    """Test niche-aware generation and revision prompts."""

    def setUp(self):
        """Prepare a representative non-AI content brief."""
        self.brief = (
            "Topic: Healthy breakfast\n"
            "Niche: Health\n"
            "Target audience: Beginners\n"
            "Content goal: Share safe breakfast education\n"
            "Key points:\n"
            "- Explain balanced breakfast components\n"
            "- Give a practical meal example\n"
            "- Share a safe preparation tip\n"
            "Hook direction: Start with a common breakfast problem\n"
            "CTA: Invite viewers to share breakfast habits"
        )

    def test_generation_prompt_uses_content_brief(self):
        """Verify generation follows the supplied niche and key points."""
        prompt = build_generation_prompt(self.brief)

        self.assertIn(self.brief, prompt)
        self.assertIn("Health", prompt)
        self.assertIn("balanced breakfast components", prompt)
        self.assertIn("breakfast habits", prompt)

    def test_generation_prompt_does_not_force_ai_content(self):
        """Verify generation does not impose AI-specific requirements."""
        prompt = build_generation_prompt(self.brief)

        self.assertIn("Do not assume the content is about AI", prompt)
        self.assertNotIn("Point 1: Explain one specific task AI can perform", prompt)

    def test_revision_prompt_preserves_content_brief(self):
        """Verify revision retains the original niche and audience."""
        prompt = build_revision_prompt(
            "HOOK: Breakfast matters.",
            ["The hook is too generic."],
            self.brief,
        )

        self.assertIn(self.brief, prompt)
        self.assertIn("preserve the exact topic, niche, target audience", prompt)
        self.assertIn("The hook is too generic.", prompt)

    def test_revision_prompt_does_not_force_ai_content(self):
        """Verify revision does not introduce unrelated AI requirements."""
        prompt = build_revision_prompt(
            "HOOK: Breakfast matters.",
            ["Improve the hook."],
            self.brief,
        )

        self.assertIn("Do not assume the content is about AI", prompt)
        self.assertNotIn("Explain one specific task AI can perform", prompt)


if __name__ == "__main__":
    unittest.main()
