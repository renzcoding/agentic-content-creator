import unittest
from unittest.mock import patch

from app.workflows.content_workflow import run_workflow


class TestContentWorkflow(unittest.TestCase):
    @patch("app.workflows.content_workflow.save_content")
    @patch("app.workflows.content_workflow.plan_content")
    def test_rejects_short_topic(self, mock_plan, mock_save):
        with patch("builtins.print") as mock_print:
            run_workflow(" AI ")

        mock_plan.assert_not_called()
        mock_save.assert_not_called()
        mock_print.assert_called_once_with(
            "Error: Topic must contain at least 5 characters."
        )


if __name__ == "__main__":
    unittest.main()
