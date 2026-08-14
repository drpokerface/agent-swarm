# Plan
1. [verified] Read constitution and setup criteria.md.
2. [verified] Swarm channel communication (propose missing manifest).
3. [verified] Write verify.py (RED) based on criteria and constitution.
4. Draft 3 script variations (script.json), evaluate against rubric, pick best.
5. Write manifest.md.
6. Run verify.py and refine the script until it passes.

# Node Tree
- Root: Goal completed [assumed]
  - C1: script.json exists and is valid JSON [assumed]
  - C2: manifest.md exists [assumed]
  - C3: Total estimated duration >= 100s [assumed]
  - C4: Contains at least 2 cutaway gags [assumed]
  - C5: LLM perception verifies it is a comedic script [assumed]
  - C6: LLM judge scores >= 7/10 on humor/pacing rubric [assumed]

# Degenerate Twins
- script.json with a single 100s scene of dead air.
- script.json with valid JSON but robotic generic dialogue.
- script.json missing visual prompts.
- manifest.md that is too short/generic.

# Facts
F1 | constitution.md exists and read | evidence: turn 1
F2 | tracer_slice.mp4 exists | evidence: turn 3
F3 | Swarm task proposed for missing manifest | evidence: turn 5
