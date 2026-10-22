import json
import re
from datetime import datetime
from pathlib import Path


OUTPUT_DIR = Path("outputs")


def save_content(
    topic: str,
    niche: str,
    plan: dict,
    script: str,
    status: str,
    issues: list[str],
) -> str:
    """Save generated content and quality results as a JSON file."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")[:50]
    filename = f"{timestamp}_{slug or 'content'}.json"
    output_path = OUTPUT_DIR / filename

    data = {
        "created_at": datetime.now().astimezone().isoformat(),
        "topic": topic,
        "niche": niche,
        "content_plan": plan,
        "script": script,
        "status": status,
        "quality_issues": issues,
    }

    output_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    return str(output_path)
