import json
from pathlib import Path


OUTPUT_DIR = Path("outputs")


def get_content_history() -> list[dict]:
    """Load saved content records, newest first."""
    if not OUTPUT_DIR.exists():
        return []

    records = []

    for path in sorted(
        OUTPUT_DIR.glob("*.json"),
        reverse=True,
    ):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
            data["filename"] = path.name
            records.append(data)
        except (json.JSONDecodeError, OSError):
            continue

    return records


def get_history_summary() -> dict:
    """Summarize saved content statuses."""
    records = get_content_history()

    return {
        "total": len(records),
        "approved": sum(
            item.get("status") == "APPROVED" for item in records
        ),
        "needs_review": sum(
            item.get("status") == "NEEDS HUMAN REVIEW"
            for item in records
        ),
    }


def get_content_by_index(index: int) -> dict | None:
    """Get a saved content record by its one-based history index."""
    records = get_content_history()

    if index < 1 or index > len(records):
        return None

    return records[index - 1]
