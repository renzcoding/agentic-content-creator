import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.tools.output_manager import save_content


class TestOutputManager(unittest.TestCase):
    def test_saves_json_markdown_and_text(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            with patch("app.tools.output_manager.OUTPUT_DIR", Path(temp_dir)):
                json_path = save_content(
                    topic="AI for Small Business",
                    niche="business",
                    plan={
                        "target_audience": "Small business owners",
                        "content_goal": "Educate",
                        "format": "Short video",
                    },
                    script="HOOK: Save time with AI.",
                    status="approved",
                    issues=[],
                )

                json_file = Path(json_path)
                markdown_file = json_file.with_suffix(".md")
                text_file = json_file.with_suffix(".txt")

                self.assertTrue(json_file.exists())
                self.assertTrue(markdown_file.exists())
                self.assertTrue(text_file.exists())

                data = json.loads(json_file.read_text(encoding="utf-8"))
                self.assertEqual(data["topic"], "AI for Small Business")
                self.assertEqual(data["status"], "approved")

                markdown = markdown_file.read_text(encoding="utf-8")
                self.assertIn("# AI for Small Business", markdown)
                self.assertIn("Small business owners", markdown)

                text = text_file.read_text(encoding="utf-8")
                self.assertEqual(text, "HOOK: Save time with AI.\n")


if __name__ == "__main__":
    unittest.main()
