import json
import tempfile
import unittest

from pathlib import Path

from app.tools.visual_asset_agent import (
    create_scene_plan,
    estimate_scene_duration,
    generate_visual_description,
    save_scene_plan,
)


class TestVisualAssetAgent(unittest.TestCase):
    def test_creates_five_scenes_from_script(self):
        script = (
            "HOOK: Kenali manfaat AI.\n"
            "BODY:\n"
            "1. Gunakan AI untuk merangkum dokumen.\n"
            "2. Gunakan AI untuk menyusun jadwal.\n"
            "3. Coba AI untuk tugas harian.\n"
            "CTA: Apa yang ingin Anda coba?"
        )

        scenes = create_scene_plan(script)

        self.assertEqual(len(scenes), 5)
        self.assertEqual(scenes[0]["section"], "HOOK")
        self.assertEqual(scenes[1]["section"], "BODY_1")
        self.assertEqual(scenes[3]["section"], "BODY_3")
        self.assertEqual(scenes[4]["section"], "CTA")
        self.assertEqual(
            scenes[1]["narration"],
            "Gunakan AI untuk merangkum dokumen.",
        )

    def test_returns_empty_list_for_invalid_script(self):
        self.assertEqual(create_scene_plan("Invalid script"), [])


    def test_save_scene_plan(self):
        scenes = [{"scene": "HOOK", "duration_seconds": 3}]

        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "scene_plan.json"
            result = save_scene_plan(scenes, str(output_path))

            self.assertTrue(output_path.exists())
            self.assertEqual(result, str(output_path))
            self.assertEqual(
                json.loads(output_path.read_text(encoding="utf-8")),
                scenes,
            )

    def test_generates_ai_visual_description(self):
        description = generate_visual_description(
            "BODY_1",
            "Gunakan AI untuk mengotomatisasi pekerjaan.",
        )
        self.assertIn("AI interface", description)


    def test_generates_cta_visual_description(self):
        description = generate_visual_description(
            "CTA",
            "Coba tips ini hari ini.",
        )
        self.assertIn("closing scene", description)

    def test_scene_duration_has_minimum_of_three_seconds(self):
        self.assertEqual(estimate_scene_duration("AI"), 3)


    def test_scene_duration_has_maximum_of_ten_seconds(self):
        narration = "word " * 100
        self.assertEqual(estimate_scene_duration(narration), 10)

if __name__ == "__main__":
    unittest.main()
