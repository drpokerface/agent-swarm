# Criteria for Script Writing & Scene Planning

## Interpretation
- The script must be written as a JSON file named `script.json` containing an array of scenes, each with shots, or a flat array of shots with scene markers.
- The total duration must be ~120 seconds. We'll target 110-130 seconds.
- The first 5 seconds must establish a strong comedic hook.
- Every shot must contain dialogue/voiceover, character visual states, background descriptions, and an estimated duration.
- No shot can have > 2.0s of dead air (i.e. empty dialogue without visual action or long pauses).

## Claims
- **C1: Valid JSON Schema**: `script.json` is valid JSON and parses as a list of scenes or shots containing the required keys: `background`, `dialogue`, `character_state`, and `duration`.
- **C2: Accurate Runtime**: The sum of durations in `script.json` is between 110 and 130 seconds.
- **C3: Early Hook (First 5s)**: The first shot(s) totaling <= 5 seconds contains a clearly marked hook or setup that instantly grabs attention.
- **C4: No Dead Air**: No shot has empty dialogue with duration > 1.5 seconds unless explicitly marked with a visual-only gag.
- **C5: Downstream Generation Readiness**: Every shot has fully specified character dialogue, character visual state, and background descriptions.
