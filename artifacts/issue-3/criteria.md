# Criteria

## Interpretation
The output is `script.json`. It must be valid JSON matching a specific schema.
The JSON must contain scenes that sum up to exactly or approximately 120 seconds (we will check if the last scene's end_time is between 110 and 130).
The JSON must pass an LLM evaluation scoring >= 4 on Joke Density, Hook Effectiveness, and Punchline Payoff based on the rubric in `spec.md`.

## Claims
- C1: `script.json` is a valid JSON file.
- C2: `script.json` has a total duration of 110 to 130 seconds.
- C3: `script.json` scores >= 4/5 on Joke Density, Hook Effectiveness, and Punchline Payoff when evaluated by a fresh LLM call against the rubric in `artifacts/issue-2/spec.md`.
