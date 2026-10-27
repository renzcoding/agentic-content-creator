
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from app.tools.voice_asset_agent import generate_voice


class TestVoiceAssetAgent(unittest.TestCase):
    """Test voice generation behavior."""

    def test_generates_audio_file(self):
        # Use a temporary directory to avoid leaving test files behind.
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = Path(temp_dir) / "voice.wav"

            # Mock eSpeak NG so the test does not require audio generation.
            with patch("app.tools.voice_asset_agent.subprocess.run") as mock_run:
                mock_run.side_effect = lambda command, **kwargs: (
                    Path(command[command.index("-w") + 1]).write_bytes(b"RIFF")
                )

                result = generate_voice(
                    "Halo, ini adalah tes suara.",
                    str(output_path),
                )

            # Verify the returned path and generated file.
            self.assertEqual(result, str(output_path))
            self.assertTrue(output_path.exists())
            mock_run.assert_called_once()

    def test_rejects_empty_narration(self):
        # Empty narration should fail before calling eSpeak NG.
        with self.assertRaises(ValueError):
            generate_voice("", "outputs/test.wav")


if __name__ == "__main__":
    # Allow this test file to run directly.
    unittest.main()
