# Plan
1. Write criteria.md and verify.py (RED). [done]
2. Study exemplars via Gemini to build real anchors. [done]
3. Generate constitution.md and manifest.md. [done]
4. Package into constitution_bundle.zip. [done]
5. Evaluate via verify.py, refine if necessary. [done]

# Node Tree
* C1: `constitution_bundle.zip` exists. [green, turn 30]
* C2: Valid zip archive. [green, turn 30]
* C3: Contains exactly constitution.md and manifest.md. [green, turn 30]
* C4: Combined word count > 500. [green, turn 30]
* C5: constitution.md sections exist. [green, turn 30]
* C6: Rubric (4, 7, 9) exists for dimensions, threshold 7. [green, turn 30]
* C7: manifest.md has filenames, formats, sample. [green, turn 30]
* C8: No placeholders/degeneracy. [green, turn 30]
* C9: Judge scores >= 7. [green, turn 30]

# Facts
F1 | Exemplars require analysis of South Park / Family Guy for real anchors. | evidence: turn 20 [verified]

# Degenerate Twins
* T1: Empty zip file.
* T2: Zip with blank files or repeated words.
* T3: Constitution lacking concrete 4/7/9 anchors.
* T4: Placeholders ('TODO', 'TBD') used instead of real content.

# Premortem
1. Rejection risk: verify.py has external dependencies that are not standard library.
   - Mitigant: verify.py imports only stdlib (zipfile, os, sys, shutil, random) and installs `google-genai` dynamically if missing, using standard subprocess calls.
2. Rejection risk: Missing sections or placeholders in constitution.md.
   - Mitigant: verify.py specifically sweeps the unpacked constitution.md and manifest.md for any placeholders (e.g. 'TODO', 'TBD', '[', ']') and fails if found. All passed.
3. Rejection risk: The ZIP archive fails to decode or contains extra/missing files.
   - Mitigant: verify.py explicitly checks that only constitution.md and manifest.md are present in the zip root, with no hidden folders or garbage files.
