## Interpretation
The goal requires generating the audio package for an animated comedy short based on script.json. 
We interpret the deliverable `audio.zip` as requiring completeness (all lines and cues) and quality.

## Criteria
C1: `audio.zip` exists in the workspace.
C2: `audio.zip` contains exactly 23 dialogue files (matching `dialogue_*.mp3` or `.wav`) and 7 SFX/Music files (matching `sfx_*.mp3` or `music_*.mp3` or `.wav`).
C3: Every file in `audio.zip` is a valid MP3 or WAV file (verified via magic bytes).
C4: A sampled dialogue audio file scores a median of >= 4/5 on a Delivery and Quality rubric across 3 independent LLM judges, anchored to professional adult animations.
