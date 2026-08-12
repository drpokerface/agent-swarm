# Criteria for Script and Asset Plan

## Interpretation
The goal is to deliver an original animated comedy short script (`script.json`) meant for 120 seconds of animation.

## Claims
* **C1 (JSON Format)**: `script.json` is a valid, parseable JSON file.
* **C2 (Schema)**: The root is an object containing a `scenes` array. Each scene contains a `background_prompt` (string) and a `dialogue` array. Each dialogue item contains `character`, `voice`, `line`, and `visual_prompt` (all strings).
* **C3 (Word Count)**: Total words in all dialogue `line` properties must be between 250 and 350 (target for ~120 seconds).
* **C4 (Subjective Quality)**: The script is judged by a blind strong LLM on Pacing, Humor, and Format. The median score from 3 runs must be >= 4.0 on all 3 dimensions.
