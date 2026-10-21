
from app.tools.niche_planner import NICHES
from app.workflows.content_workflow import run_workflow


def main() -> None:
    """Run the content creation workflow."""
    print("Available niches:")

    for key, name in NICHES.items():
       print(f"- {key}: {name['name']}")

    niche = input("Choose a niche key: ").strip().lower()

    if niche not in NICHES:
        print("Error: Invalid niche.")
        return

    topic = input("Enter a content topic: ").strip()

    if not topic:
        print("Error: Topic cannot be empty.")
        return

    run_workflow(topic, niche)


if __name__ == "__main__":
    main()
