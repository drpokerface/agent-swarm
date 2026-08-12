# Criteria for Tracer Slice and Capabilities Probe

## Interpretation
The goal is to deliver a 10-second end-to-end slice of an animated comedy short (1280x720, MP4, synced TTS audio) and a capabilities report detailing the generation tools probed.

## Claims
- **C1: Package Exists**: slice_package.zip must exist at the workspace root.
- **C2: Package Contents**: slice_package.zip contains exactly capabilities.md and slice.mp4.
- **C3: Capabilities Content**: capabilities.md is a non-empty file that explicitly mentions 'limit' or 'limits' to satisfy the API limits documentation requirement.
- **C4: Video Specs**: slice.mp4 is a valid MP4 video, duration between 8 and 15 seconds, strictly 1280x720 resolution, with at least one video stream and at least one audio stream (checked via ffprobe).
- **C5: Judgment Score**: A fresh blind judge (gemini-3.5-flash) evaluating the slice.mp4 or extracted assets scores the visual clarity, pacing, and tone at >= 3/5 based on the spec.md rubric.
