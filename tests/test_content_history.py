import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.tools.content_history import (
    get_content_by_index,
    get_content_history,
    get_history_summary,
)


class TestContentHistory(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.output_dir = Path(self.temp_dir.name)
        self.patcher = patch(
            "app.tools.content_history.OUTPUT_DIR",
            self.output_dir,
        )
        self.patcher.start()

    def tearDown(self):
        self.patcher.stop()
        self.temp_dir.cleanup()

    def create_record(self, filename, status):
        (self.output_dir / filename).write_text(
            json.dumps({"status": status}),
            encoding="utf-8",
        )

    def test_returns_empty_when_directory_is_missing(self):
        self.patcher.stop()
        with patch(
            "app.tools.content_history.OUTPUT_DIR",
            self.output_dir / "missing",
        ):
            self.assertEqual(get_content_history(), [])
        self.patcher.start()

    def test_returns_newest_filename_first(self):
        self.create_record("20261001_old.json", "APPROVED")
        self.create_record("20261002_new.json", "APPROVED")

        records = get_content_history()

        self.assertEqual(
            [record["filename"] for record in records],
            ["20261002_new.json", "20261001_old.json"],
        )

    def test_skips_invalid_json(self):
        (self.output_dir / "20261001_bad.json").write_text(
            "{invalid",
            encoding="utf-8",
        )
        self.create_record("20261002_good.json", "APPROVED")

        self.assertEqual(len(get_content_history()), 1)

    def test_summarizes_statuses(self):
        self.create_record("1.json", "APPROVED")
        self.create_record("2.json", "NEEDS HUMAN REVIEW")
        self.create_record("3.json", "REJECTED")

        self.assertEqual(
            get_history_summary(),
            {"total": 3, "approved": 1, "needs_review": 1},
        )

    def test_gets_record_by_one_based_index(self):
        self.create_record("1.json", "APPROVED")
        self.create_record("2.json", "REJECTED")

        self.assertEqual(
            get_content_by_index(1)["status"],
            "REJECTED",
        )
        self.assertIsNone(get_content_by_index(0))
        self.assertIsNone(get_content_by_index(3))


if __name__ == "__main__":
    unittest.main()
