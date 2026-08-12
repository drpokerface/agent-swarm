# Notes

## Goal
Generate `script.json` representing a ~120-second animated comedy short.

## Plan
1. [GREEN] Create criteria.md, notes.md, and verify.py. (Turn 3)
2. [GREEN] Run verify.py to confirm it fails when script.json is missing. (Turn 3)
3. [GREEN] Write generator script using Gemini API to draft a hilarious, structured script following the guidelines. (Turn 4)
4. [GREEN] Run verify.py on the generated script. (Turn 5)
5. [GREEN] Refine and judge the comedy and structure using Gemini Pro as an outside anchor judge. (Turn 70)
6. [GREEN] Test verify.py's fault proof and execute the final gate checks. (Turn 70)

## Node Tree
- ROOT: script.json conforms to criteria.md | GREEN (Turn 70)
  - C1: Valid JSON | GREEN (Turn 70)
  - C2: Duration (110-130s) | GREEN (Turn 70)
  - C3: 5s Hook Flagged | GREEN (Turn 70)
  - C4: No Dead Air | GREEN (Turn 70)
  - C5: Visual/Audio Prompts | GREEN (Turn 70)
  - C6: Adult Comedy Style | GREEN (Turn 70)

## Facts
- F1 | script.json has exactly 24 shots summing to 120.0 seconds. | Turn 70
- F2 | The 5s hook is correctly flagged in the first shot. | Turn 70
- F3 | Subjective evaluation achieves score of 8/10 from gemini-3.1-pro-preview. | Turn 70
