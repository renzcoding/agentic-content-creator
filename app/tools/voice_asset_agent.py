
import subprocess
from pathlib import Path


def generate_voice(
    narration: str,
    output_path: str,
    voice: str = "id",
    speed: int = 150,
) -> str:
    """Convert narration into a WAV audio file using eSpeak NG."""
    # Reject empty narration to avoid generating meaningless audio.
    if not narration.strip():
        raise ValueError("Narration must not be empty.")

    # Create the output directory when it does not exist.
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)

    # Run eSpeak NG and save the generated speech as a WAV file.
    subprocess.run(
        [
            "espeak-ng",
            "-v", voice,
            "-s", str(speed),
            "-w", str(path),
            narration,
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    # Return the path so other workflow components can use the audio.
    return str(path)
