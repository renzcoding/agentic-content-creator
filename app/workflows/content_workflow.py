from app.tools.output_manager import save_content

from app.tools.niche_planner import plan_content
from app.tools.script_generator import generate_script, revise_script
from app.tools.quality_checker import quality_check
from app.tools.visual_asset_agent import create_scene_plan, save_scene_plan
from app.tools.voice_asset_agent import generate_voice
from config.settings import MAX_REVISION_ATTEMPTS


def run_workflow(topic: str, niche: str = "tech") -> None:
    """Plan, generate, evaluate, and revise content."""
    if len(topic.strip()) < 5:
        print("Error: Topic must contain at least 5 characters.")
        return
    plan = plan_content(topic, niche)

    print("\nCONTENT PLAN:")
    for key, value in plan.items():
        print(f"{key}: {value}")

    brief = (
        f"Topic: {plan['topic']}\n"
        f"Niche: {plan['niche']}\n"
        f"Audience: {plan['target_audience']}\n"
        f"Key points: {', '.join(plan['key_points'])}\n"
        f"Hook: {plan['hook_direction']}\n"
        f"CTA: {plan['cta']}"
    )

    script = generate_script(brief)
    best_script = script
    best_issue_count = float("inf")

    for attempt in range(1, MAX_REVISION_ATTEMPTS + 1):
        result = quality_check(script, topic)
        issue_count = len(result["issues"])

        print(f"\nAttempt: {attempt}")
        print(f"Quality check: {result}")

        if result["approved"]:
            print("\nSTATUS: APPROVED")
            print("\nFINAL SCRIPT:")
            print(script)

            output_path = save_content(
                topic, niche, plan, script, "APPROVED", []
            )
            print(f"Saved output: {output_path}")

            scenes = create_scene_plan(script)
            if scenes:
                scene_path = output_path.rsplit(".", 1)[0] + "_scene_plan.json"
                save_scene_plan(scenes, scene_path)
                print(f"Saved scene plan: {scene_path}")

                voice_path = output_path.rsplit(".", 1)[0] + "_voice.wav"
                try:
                    generate_voice(script, voice_path)
                    print(f"Saved voice audio: {voice_path}")
                except (OSError, ValueError) as error:
                    print(f"Voice generation failed: {error}")

            return

        if issue_count < best_issue_count:
            best_script = script
            best_issue_count = issue_count
        elif attempt > 1:
            print("Revision did not improve quality. Stopping.")
            break

        if attempt < MAX_REVISION_ATTEMPTS:
            print("Revising script with local LLM...")
            script = revise_script(script, result["issues"], brief)

    print("\nSTATUS: NEEDS HUMAN REVIEW")
    print("No valid script passed quality checks.")
    print("\nBEST DRAFT:")
    print(best_script)
    print("\nREMAINING ISSUES:")
    remaining_issues = quality_check(best_script, topic)["issues"]
    print(remaining_issues)

    output_path = save_content(
        topic, niche, plan, best_script,
        "NEEDS HUMAN REVIEW", remaining_issues
    )
    print(f"Saved output: {output_path}")


if __name__ == "__main__":
    from app.tools.niche_planner import NICHES

    print("Available niches:")
    for key, name in NICHES.items():
        print(f"- {key}: {name['name']}")

    niche = input("Choose a niche key: ").strip().lower()
    topic = input("Enter a content topic: ").strip()

    if niche not in NICHES:
        print("Error: Invalid niche.")
    elif not topic:
        print("Error: Topic cannot be empty.")
    else:
        run_workflow(topic, niche)
