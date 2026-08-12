## Interpretation
The goal asks for a "Tracer Slice and Capabilities Probe".
1. We must probe TTS, image generation, and video assembly capabilities and document them in `capabilities.md`, including API limits.
2. We must build a tiny but complete 10-second end-to-end version of a single gag (`slice.mp4`, 1280x720, synced audio).
3. Package both into `slice_package.zip`.

Claims:
C1: slice_package.zip exists and contains exactly capabilities.md and slice.mp4.
C2: capabilities.md contains the words "limit" or "limits" and mentions API models/tools.
C3: slice.mp4 is a valid video file.
C4: slice.mp4 has exactly a 1280x720 resolution video stream.
C5: slice.mp4 has at least one audio stream (synced TTS).
C6: slice.mp4 scores >= 3/5 on the visual/audio/comedy adult-animation style check via an LLM judge.
