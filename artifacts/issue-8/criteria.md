# Criteria
## Interpretation
The goal requires probing capabilities (TTS, Image, Video) using available API keys (Gemini), documenting them in capabilities.md, and producing a 10s slice.mp4 (1280x720, synced audio). Both go into slice_package.zip.

## Claims
C1: slice_package.zip exists.
C2: slice_package.zip contains capabilities.md and slice.mp4.
C3: slice.mp4 is a valid video file with 1280x720 resolution.
C4: slice.mp4 contains an audio track.
C5: slice.mp4 scores >= 3/5 against the spec.md rubric using an LLM judge.
