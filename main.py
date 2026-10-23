from pathlib import Path

from app.tools.niche_planner import NICHES
from app.tools.content_history import get_content_history, get_content_by_index, get_history_summary
from app.workflows.content_workflow import run_workflow


def create_content() -> None:
    print("\nAvailable niches:")

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


def show_history() -> None:
    records = get_content_history()
    print(f"\nContent history: {len(records)} records")

    if not records:
        print("No content history found.")
        return

    for index, item in enumerate(records, 1):
        print(
            f"{index}. [{item.get('status', 'UNKNOWN')}] "
            f"{item.get('topic', 'Untitled')} "
            f"({item.get('niche', 'N/A')})"
        )

    choice = input("\nEnter a number to view details, or press Enter to return: ").strip()

    if not choice:
        return

    if not choice.isdigit():
        print("Error: Please enter a valid number.")
        return

    item = get_content_by_index(int(choice))

    if item is None:
        print("Error: Content not found.")
        return

    print(f"\nTopic: {item.get('topic', 'Untitled')}")
    print(f"Status: {item.get('status', 'UNKNOWN')}")
    print(f"Niche: {item.get('niche', 'N/A')}")
    print(f"\nScript:\n{item.get('script', 'No script available')}")
    text_filename = Path(item.get("filename", "")).with_suffix(".txt").name
    print(f"Text file: outputs/{text_filename}")

def main() -> None:
    while True:
        summary = get_history_summary()
        print(
            f"\nStats: {summary['total']} total | "
            f"{summary['approved']} approved | "
            f"{summary['needs_review']} needs review"
        )
        print("\n=== Agentic Content Creator ===")
        print("1. Create content")
        print("2. View content history")
        print("3. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            create_content()
        elif choice == "2":
            show_history()
        elif choice == "3":
            print("Goodbye!")
            break
        else:
            print("Error: Invalid option.")


if __name__ == "__main__":
    main()