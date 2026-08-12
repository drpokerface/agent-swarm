# Criteria

## Interpretation
The goal is to produce an original 2-minute animated comedy script formatted as `script.json`. The script needs precise duration constraints, word counts for pacing, specific structural beats (hook in the first 5s, strong punchline at the end), and must be evaluated against the provided `spec.md` rubric by a blind judge.

## Claims
C1: File `script.json` exists, is valid JSON, and matches the schema (list of scenes, each with `duration_seconds` and a `dialogue` list containing `character`, `voice`, `line`, `visual_prompt`).
C2: Total duration across all scenes is exactly 120 seconds.
C3: Total spoken words (sum of words in `line` fields) is between 250 and 350.
C4: The script contains a hook (`"tag": "hook"`) within the first 5 seconds, and a punchline (`"tag": "punchline"`).
C5: A blind judge (`gemini-3.5-pro`) scores the script's humor, hook, and punchline against `spec.md`. The median score of 3 samples is >= 7/10, and it strictly beats the lazy baseline.
