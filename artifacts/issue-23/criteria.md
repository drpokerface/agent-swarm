# Criteria for Final Integration and Polish

## Interpretation
The goal is to assemble an animated comedy short using `script.json` and `assets.zip` contents, achieving a ~120s runtime at 1280x720.
The video must contain distinct audio and video streams, and be evaluated for subjective quality against a threshold of 7 based on the constitution rubric.

## Claims
- **C1**: `final.mp4` exists.
- **C2**: `final.mp4` contains distinct audio and video streams.
- **C3**: `final.mp4` resolution is exactly 1280x720.
- **C4**: `final.mp4` duration is between 100 and 140 seconds (~120s).
- **C5**: `final.mp4` is non-degenerate (not blank, silent, or static noise) via a model perception check.
- **C6**: The subjective score of the artifact is >= 7 against the constitution rubric.
