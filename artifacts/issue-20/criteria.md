# Criteria

## Interpretation
- **Tracer Slice**: A ~10-second (5s to 15s) completed end-to-end animated short version of a scene, including character voice and cutaway, compiled as a 1280x720 MP4 with audio.
- **Fast-paced adult-comedy style**: Needs comedic timing, no dead air, and recognizable adult animation aesthetic (similar to Family Guy/South Park).
- **Manifest and Capabilities**: Integration manifest listing artifacts, formats, and samples, and a capability.md detailing probe findings for TTI, TTS, and video models.
- **Subjective Threshold**: Must score >= 7 out of 10 against the constitution rubric using a fresh comparative model-based judge sample.

## Claims
- **C1**: `tracer_slice.mp4` exists, is 1280x720 resolution, has video and audio tracks, and is 5-15 seconds in duration.
- **C2**: `capabilities.md` exists and lists API choices, TTI/TTS/Video capabilities, and details of the probe findings.
- **C3**: `manifest.md` exists and serves as a valid integration contract detailing filenames, formats, and samples.
- **C4**: `tracer_slice.mp4` contains non-degenerate actual content (not blank, silent, or uniform).
- **C5**: Perceptual check: fresh model-perception call confirms the video depicts animated characters with synced audio matching the script, and scores >= 7 on the comedy/animation rubric.
