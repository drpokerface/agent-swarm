# Plan
1. [x] Distill anchors via web search (turn 3)
2. [x] Write criteria.md (turn 4)
3. [x] Write verify.py (RED) (turn 5)
4. [x] Generate constitution.md (turn 6)
5. [x] Evaluate and improve (turn 70)
6. [x] Ship (turn 73)

# Node Tree
- C1: `constitution.md` exists [verified] (turn 72)
- C2: Includes strategy/style/conventions [verified] (turn 72)
- C3: Contains 4,7,9 rubrics for timing/visual/pacing [verified] (turn 72)
- C4: Mandates manifest.md [verified] (turn 72)
- C5: No placeholders [verified] (turn 72)
- C6: Subjective score >= 7 [verified] (turn 72)

# Degenerate Twins
1. Empty or missing file.
2. Contains text but misses required structural elements (manifest mandate, rubrics).
3. Contains synthetic placeholder text ("TODO", "[insert]").
4. Low quality/hollow constitution that does not align with the provided anchors.

# Facts
- F1 | Anchors distilled | evidence: turn 3
- F2 | criteria.md exists | evidence: turn 4
- F3 | verify.py runs and passes | evidence: turn 72
- F4 | manifest.md exists | evidence: turn 70

# PREMORTEM
1. GATE REJECTION: `verify.py` fails to catch a degenerate twin.
   - *Fix applied*: Our `verify.py` checks for the presence of every required concept (strategy, rubrics, 4/7/9, manifest mandate) AND performs a model-based subjective evaluation.
2. GATE REJECTION: FAULT-PROOF is hardcoded to a specific file or doesn't generate fresh randomness.
   - *Fix applied*: I have checked `verify.py` to ensure the fault is injected into a randomly named file in `scratch/`.
3. GATE REJECTION: Missing or truncated required files.
   - *Fix applied*: I've validated file lengths and am explicitly reading `criteria.md` to ensure it is fully intact and ends with the correct terminology.
