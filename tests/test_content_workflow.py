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

    @patch("app.workflows.content_workflow.save_content")
    @patch("app.workflows.content_workflow.quality_check")
    @patch("app.workflows.content_workflow.generate_script")
    @patch("app.workflows.content_workflow.plan_content")
    @patch("app.workflows.content_workflow.save_scene_plan")
    @patch("app.workflows.content_workflow.create_scene_plan")
    def test_saves_approved_script(
        self, mock_plan_scenes, mock_save_scenes,
        mock_plan, mock_generate, mock_quality, mock_save
    ):
        mock_plan.return_value = {
            "topic": "AI for business",
            "niche": "tech",
            "target_audience": "Business owners",
            "key_points": ["Automation"],
            "hook_direction": "Ask a question",
            "cta": "Try this today",
        }
        mock_generate.return_value = "HOOK: Use AI to save time."
        mock_quality.return_value = {
            "approved": True,
            "issues": [],
        }

        with patch("builtins.print"):
            run_workflow("AI for business", "tech")

        mock_save.assert_called_once_with(
            "AI for business",
            "tech",
            mock_plan.return_value,
            mock_generate.return_value,
            "APPROVED",
            [],
        )

        mock_plan_scenes.assert_called_once_with(
            mock_generate.return_value
        )
        mock_save_scenes.assert_called_once_with(
            mock_plan_scenes.return_value,
            unittest.mock.ANY,
        )


    @patch("app.workflows.content_workflow.save_content")
    @patch("app.workflows.content_workflow.quality_check")
    @patch("app.workflows.content_workflow.generate_script")
    @patch("app.workflows.content_workflow.plan_content")
    def test_saves_script_for_human_review(
        self, mock_plan, mock_generate, mock_quality, mock_save
    ):
        mock_plan.return_value = {
            "topic": "AI for business",
            "niche": "tech",
            "target_audience": "Business owners",
            "key_points": ["Automation"],
            "hook_direction": "Ask a question",
            "cta": "Try this today",
        }
        mock_generate.return_value = "Draft script for review."
        
        mock_quality.return_value = {
            "approved": False,
            "issues": ["Weak hook"],
        }

        with patch(
            "app.workflows.content_workflow.MAX_REVISION_ATTEMPTS", 1
        ), patch("builtins.print"):
            run_workflow("AI for business", "tech")

        mock_save.assert_called_once_with(
            "AI for business",
            "tech",
            mock_plan.return_value,
            mock_generate.return_value,
            "NEEDS HUMAN REVIEW",
            ["Weak hook"],
        )


if __name__ == "__main__":
    unittest.main()
