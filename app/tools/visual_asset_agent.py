import re
import json
from pathlib import Path

def generate_visual_description(section: str, narration: str) -> str:
    """Generate a basic visual direction from scene narration."""
    text = narration.lower()

    if section == "HOOK":
        return f"Create an attention-grabbing opening visual for: {narration}"

    if section == "CTA":
        return "Show a clean closing scene with space for a call-to-action caption."

    if any(word in text for word in ["ai", "artificial intelligence", "otomatisasi"]):
        return "Show an AI interface or automation workflow relevant to the narration."

    if any(word in text for word in ["bisnis", "usaha", "pelanggan", "penjualan"]):
        return "Show a small business owner working with customers or reviewing sales."

    if any(word in text for word in ["waktu", "produktif", "efisien"]):
        return "Show a person organizing tasks or completing work efficiently."

    return f"Show a realistic, relevant example of: {narration}"


def estimate_scene_duration(narration: str) -> int:
    """Estimate scene duration based on narration length."""
    word_count = len(narration.split())
    duration = round(word_count / 2.5)
    return max(3, min(duration, 10))

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
                    "visual_description": generate_visual_description(
                        "HOOK", narration,
                    ),
                    "duration_seconds": estimate_scene_duration(narration),
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
                    "visual_description": generate_visual_description(
                        "CTA", narration
                    ),
                    "duration_seconds": estimate_scene_duration(narration),
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
                    "visual_description": generate_visual_description(
                        f"BODY_{point_number}", match.group(1).strip()
                    ),
                    "duration_seconds": estimate_scene_duration(match.group(1).strip()),
                })

    return scenes


def save_scene_plan(scenes: list[dict], output_path: str) -> str:
    """Save a scene plan as a JSON file."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(scenes, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return str(path)