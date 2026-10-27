import re

def create_scene_plan(script: str) -> list[dict]:
    """Convert a script into a visual plan for short-form video scenes."""
    scenes = []
    section = None

    for line in script.splitlines():
        line = line.strip()

        if line.startswith("HOOK:"):
            section = "HOOK"
            narration = line[len("HOOK:"):].strip()
            if narration:
                scenes.append({
                    "scene": len(scenes) + 1,
                    "section": "HOOK",
                    "narration": narration,
                    "visual_description": (
                        "Show an opening visual related to the topic."
                    ),
                    "duration_seconds": 3,
                })

        elif line == "BODY:":
            section = "BODY"

        elif line.startswith("CTA:"):
            section = "CTA"
            narration = line[len("CTA:"):].strip()
            if narration:
                scenes.append({
                    "scene": len(scenes) + 1,
                    "section": "CTA",
                    "narration": narration,
                    "visual_description": (
                        "Show a closing visual with space for a CTA caption."
                    ),
                    "duration_seconds": 3,
                })

        elif section == "BODY":
            match = re.match(r"^\d+\.\s*(.+)$", line)
            if match:
                point_number = sum(
                    item["section"].startswith("BODY_")
                    for item in scenes
                ) + 1
                scenes.append({
                    "scene": len(scenes) + 1,
                    "section": f"BODY_{point_number}",
                    "narration": match.group(1).strip(),
                    "visual_description": (
                        "Show a clear visual example of this practical point."
                    ),
                    "duration_seconds": 5,
                })

    return scenes