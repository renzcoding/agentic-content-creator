# M35 - Niche-Aware Script Generation

## Objective

Make script generation and revision follow the supplied content brief, including its topic, niche, target audience, and content goal.

## Problem

The previous script generation prompt contained AI-specific requirements.

This made the generator unsuitable for other content niches, such as health, religion, food, business, sports, and music.

The revision prompt also needed stronger instructions to preserve the original content brief during script improvement.

## Implementation

Updated `app/tools/script_generator.py`.

Changes:
- Added `build_generation_prompt()` to construct generation prompts from the supplied content brief.
- Added `build_revision_prompt()` to construct revision prompts using the original script, quality issues, and content brief.
- Removed forced AI-specific content requirements.
- Added instructions to preserve the exact topic, niche, target audience, and content goal during revision.
- Kept Indonesian short-form script requirements, including HOOK, BODY, and CTA.
- Preserved the existing Ollama integration through the local generation API.
- Preserved `clean_script()` for removing placeholder labels.
- Preserved `trim_script()` for limiting script section lengths.
- Preserved the revision error-handling fallback.

## Tests

Added `tests/test_script_generator.py` with four tests:

1. `test_generation_prompt_uses_content_brief`
   - Verifies generation follows the supplied niche and key points.
2. `test_generation_prompt_does_not_force_ai_content`
   - Verifies generation does not impose AI-specific requirements.
3. `test_revision_prompt_preserves_content_brief`
   - Verifies revision retains the original brief and quality feedback.
4. `test_revision_prompt_does_not_force_ai_content`
   - Verifies revision does not introduce unrelated AI requirements.

## Validation

- Script generator tests: 4 passed.
- Python syntax compilation: passed.
- Full test suite: 153 passed.

## Result

Script generation and revision now adapt to the supplied content brief instead of assuming every video is about AI. The existing Ollama integration and script-processing functions remain available.
