## Interpretation
We are researching and establishing a Comedy Animation Specification for a ~2-minute adult animated comedy short.
The specification must be recorded in `spec.md`.
It must list the measurable properties of successful adult comedy animations (e.g., South Park, Family Guy) that we researched.
It must define a detailed scoring rubric with 1-5 anchored descriptors for 4 categories:
1. Script Humor & Pacing
2. Audio Punchiness & Delivery
3. Visual Cohesion (Cutout Style)
4. Overall Editing & Timing

To verify this, our `verify.py` script will parse `spec.md` and check:
- Presence of the file.
- Presence of all 4 categories.
- Presence of distinct descriptors for Score 1, Score 2, Score 3, Score 4, and Score 5 in each of the 4 categories.
- Ensure a fault-proof mechanism runs correctly by corrupting a scratch copy and detecting the failure.

## Claims
C1: File `spec.md` exists.
C2: `1. Script Humor & Pacing` section is present with distinct Score 1-5 descriptors.
C3: `2. Audio Punchiness & Delivery` section is present with distinct Score 1-5 descriptors.
C4: `3. Visual Cohesion (Cutout Style)` section is present with distinct Score 1-5 descriptors.
C5: `4. Overall Editing & Timing` section is present with distinct Score 1-5 descriptors.
C6: Research and measurable properties of satirical adult-animation are documented in the specification.
