## Interpretation
- "Adult animation style": Fast-paced, cynical, absurd situations, high joke density (e.g., Family Guy, South Park).
- "2 minutes": Approximately 120 seconds, so >= 100 seconds is acceptable.
- "Zero dead air": Scene JSON must explicitly account for continuous pacing.
- "Integration Contract": manifest.md is required.

## Claims
- C1: `script.json` exists, is valid JSON, and contains an array of scene objects.
- C2: `manifest.md` exists and describes the JSON schema of `script.json`.
- C3: Total `duration` across all scenes in `script.json` is >= 100 seconds.
- C4: The script contains at least two distinct "cutaway" gags.
- C5: LLM perception confirms the text is a comedic script with dialogue and visual prompts.
- C6: LLM judge scores >= 7/10 on humor and pacing against the constitution rubric.
