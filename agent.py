
from typing import Callable


def generate_script(topic: str) -> str:
    """Generate a draft for a short-form content video."""
    return (
        f"HOOK: Avoid these 3 mistakes when learning {topic}!\n"
        f"BODY: Learn the fundamentals of {topic}, practice consistently, "
        "and evaluate your results.\n"
        "CTA: Follow for more practical tips!"
    )


def quality_check(script: str) -> dict:
    """Evaluate the quality of a content draft."""
    issues = []

    if len(script) < 100:
        issues.append("The script is too short.")

    if "HOOK:" not in script:
        issues.append("The hook is missing.")

    if "CTA:" not in script:
        issues.append("The call to action is missing.")

    return {
        "approved": len(issues) == 0,
        "issues": issues,
    }


def run_agent(topic: str, max_attempts: int = 3) -> None:
    """Execute the agent loop: act, evaluate, and decide."""
    tools: dict[str, Callable] = {
        "generate_script": generate_script,
        "quality_check": quality_check,
    }

    script = ""

    for attempt in range(1, max_attempts + 1):
        print(f"\n--- ATTEMPT {attempt} ---")

        # DECIDE: Generate a draft if one does not exist.
        if not script:
            selected_tool = "generate_script"
            script = tools[selected_tool](topic)
            print(f"Selected tool: {selected_tool}")

        # OBSERVE: Evaluate the current draft.
        selected_tool = "quality_check"
        result = tools[selected_tool](script)

        print(f"Selected tool: {selected_tool}")
        print(f"Quality check result: {result}")

        # DECIDE: Stop if the draft passes quality checks.
        if result["approved"]:
            print("\nSTATUS: APPROVED")
            print("\nFINAL SCRIPT:")
            print(script)
            return

        # ACT: Revise the draft if quality checks fail.
        print("Quality check failed. Revising the draft.")

        script += (
            "\nADDITIONAL BODY: Include one practical example "
            "that viewers can apply."
        )

    print("\nSTATUS: NEEDS HUMAN REVIEW")


if __name__ == "__main__":
    topic = input("Enter a content topic: ")
    run_agent(topic)
