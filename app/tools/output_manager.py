
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
    """Save generated content as JSON and Markdown."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r"[^a-z0-9]+", "_", topic.lower()).strip("_")[:50]
    filename = f"{timestamp}_{slug or 'content'}"
    json_path = OUTPUT_DIR / f"{filename}.json"
    markdown_path = OUTPUT_DIR / f"{filename}.md"
    text_path = OUTPUT_DIR / f"{filename}.txt"

    data = {
        "created_at": datetime.now().astimezone().isoformat(),
        "topic": topic,
        "niche": niche,
        "content_plan": plan,
        "script": script,
        "status": status,
        "quality_issues": issues,
    }

    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    markdown = (
        f"# {topic}\n\n"
        f"- **Niche:** {niche}\n"
        f"- **Status:** {status}\n"
        f"- **Created:** {data['created_at']}\n\n"
        f"## Content Plan\n\n"
        f"- **Audience:** {plan.get('target_audience', '')}\n"
        f"- **Goal:** {plan.get('content_goal', '')}\n"
        f"- **Format:** {plan.get('format', '')}\n\n"
        f"## Script\n\n{script}\n\n"
        f"## Quality Issues\n\n"
        + (
            "\n".join(f"- {issue}" for issue in issues)
            if issues
            else "- None"
        )
        + "\n"
    )

    markdown_path.write_text(markdown, encoding="utf-8")
    text_path.write_text(script.strip() + "\n", encoding="utf-8")
    return str(json_path)
