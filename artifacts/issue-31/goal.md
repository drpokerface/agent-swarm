Tracer Slice and Capabilities Probe

SHARED SPEC: All tasks must adhere to an irreverent, fast-paced adult-animation comedy style (e.g., South Park, Family Guy). Pacing must be punchy with no dead air. Humor relies on clear setup, absurd escalation, and strong punchline. Visuals are 1280x720. Audio must be clear, synced, and leveled. Placeholders are strictly forbidden. END SHARED SPEC. Open and validate constitution_bundle.zip against its manifest.md FIRST; input-reject through your swarm channel if rotten. HARDEST FIRST: The riskiest assumption is that our autonomous environment can programmatically generate coherent character visuals, TTS audio, and sync them into a valid MP4 using accessible APIs without human UI interaction. PROBE for the strongest generation tools and models your API keys can reach for images and speech. Primitive fallbacks like hand-drawn shapes are forbidden unless your probe proves no better tier is reachable. Record findings in capabilities.md. Build a TINY but COMPLETE end-to-end 10-second slice (slice.mp4) of the final deliverable with one scene, one voiced line, one cut, assembled exactly the way the final task will assemble it. Judge it against the exemplars from the constitution. Package capabilities.md, slice.mp4, and manifest.md (with exact filenames, formats, and a tiny sample) into tracer_bundle.zip. This bundle defines the file naming, formats, quality floor, and assembly method for the whole board. JUDGMENT: Mechanical facts - zip exists, decodes, slice.mp4 duration ~10s, contains audio/video streams. Subjective quality - 0-10 score against the constitution's anchored rubric (Pass >= 7). verify.py must decode the actual MP4, and include one cheap model-perception call confirming the sampled video depicts an animated character and synced voice. Placeholder or stub content anywhere is an automatic FAIL.

Save the main deliverable as tracer_bundle.zip.

Already provided in your working directory: artifacts/issue-30/constitution_bundle.zip

SWARM CHANNEL: you are working issue #31 of the GitHub repo drpokerface/agent-swarm (token in GITHUB_TOKEN env). If you discover work this plan is missing, you may post ONE comment on your own issue via the API starting exactly 'PROPOSE-TASK: ' (state: title, why, which existing deliverable it unblocks, what it produces). Facing an irreversible, genuinely ambiguous choice, you may post ONE comment starting exactly 'QUESTION: ', then continue on the reversible path without waiting. If a PROVIDED input artifact fails your validation (placeholder, degenerate, or broken contract), post ONE comment starting exactly 'INPUT-REJECT: #<producing issue number> ' plus one line of evidence - the swarm will reopen that task; then declare impossible honestly instead of building on garbage. Never create issues yourself; an owner-side arbiter reviews and answers as an 'ARBITER re' comment on this issue.

LAST VERIFICATION FAILURE (repair this first):
VERIFY: FAIL by aditya-laptop (drpokerface)

--- verify.py output tail ---
```
EXPECT: verify.py executes C1-C5 checks and confirms validity
FAULT-PROOF: Successfully caught induced C1/C3 fault! Result: {'C1': False, 'C2': False, 'C3': False, 'C4': False, 'C5': False}
C1: True
C2: False
C3: True
C4: False
C5: False
Details: C2 Failed: imageio error maximum recursion depth exceeded while calling a Python object; Perceptual checks skipped: API key or mechanical preconditions missing
VERDICT: FAIL

```
