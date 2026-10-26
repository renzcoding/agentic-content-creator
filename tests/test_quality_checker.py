import unittest

from app.tools.quality_checker import quality_check
from main import is_valid_topic


class TestQualityChecker(unittest.TestCase):
    def test_rejects_short_topic(self):
        self.assertFalse(is_valid_topic("AI"))

    def test_accepts_valid_topic(self):
        self.assertTrue(is_valid_topic("AI tools"))

    def test_rejects_empty_script(self):
        result = quality_check("")
        self.assertFalse(result["approved"])

    def test_rejects_irrelevant_topic(self):
        script = """HOOK: Learn something new today.
BODY:
1. Reading books can improve your knowledge every day.
2. Practice skills regularly to build confidence.
3. Share useful lessons with other people.
CTA: What new skill will you learn today?"""
        result = quality_check(script, "quantum computing")
        self.assertFalse(result["approved"])

    def test_accepts_valid_structure(self):
        script = """HOOK: Want to use AI more effectively?
BODY:
1. Use AI tools to summarize long documents quickly.
2. Ask AI to organize tasks into a clear daily schedule.
3. Review AI suggestions before applying them to your work.
CTA: How will you use AI to improve your workflow?"""
        result = quality_check(script, "AI")
        self.assertIn("approved", result)


if __name__ == "__main__":
    unittest.main()
