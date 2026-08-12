# Criteria for Script Writing & Scene Planning

## Interpretation
The overarching goal is to generate an original, hilarious, animated comedy short (~120 seconds). The deliverables require specific structural constraints (5s hook, no dead air, explicit audio/visual prompts for a downstream generator pipeline). 
Crucially, the script must embody an "irreverent, satirical adult-animation style" and have a "high quality bar for comedic timing" based on the prompt.

## Anchors of Excellence for Adult Comedy Style
1. **South Park:** Master of satirical, irreverent comedy that uses absurdity to mock societal norms.
2. **Family Guy:** Known for fast-paced scenes, random pop-culture references, and distinct punchlines.
3. **Rick and Morty:** Showcases dark comedy, witty banter, and contrasts high sci-fi stakes with mundane family reactions.

*Lazy Baseline:* A hollow script where characters speak literal, boring dialogue with no jokes, no satire, and no comedic timing (e.g., just describing their actions or standing around talking blandly).

## Claims
* **C1:** `script.json` is a perfectly formatted JSON array.
* **C2:** The total `duration` of all scenes is exactly between 110 and 130 seconds.
* **C3:** A `hook` flag is true for at least one shot starting within the first 5 seconds.
* **C4:** There is no "dead air" (no shots > 1s lacking dialogue without dynamic visual descriptions).
* **C5:** Every shot explicitly defines `character`, `dialogue`, `visual_state`, `background`, `duration`, and `hook`.
* **C6:** The script meets a high bar for Adult Comedy Style. Evaluated by a fresh, blinded LLM judge (Gemini Pro) assessing the script against the Anchors of Excellence and the Lazy Baseline. A median score of >= 7/10 across 3 independent evaluations is required to pass.
