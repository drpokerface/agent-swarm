# Criteria
## Interpretation
The goal is to perform a tracer slice and capabilities probe. We must:
1. Audit the tools and APIs available in this environment (TTS, Image, Video) and document them in `capabilities.md`.
2. Build a tiny but complete end-to-end video named `slice.mp4` (1280x720, synced audio, 10 seconds, featuring one scene, one voiced line, one visual cut/change) using these tools.
3. Implement a robust verify.py that verifies these claims, including a fault-proof check on a corrupted/broken copy under scratch/.

## Claims
- C1: `capabilities.md` exists and contains a thorough audit of available tools/APIs (TTS, Image, Video) and setups.
- C2: `slice.mp4` exists in the root directory.
- C3: `slice.mp4` has exactly 1280x720 resolution.
- C4: `slice.mp4` contains active video and active audio streams.
- C5: `slice.mp4` has a duration of 8.0 to 15.0 seconds.
- C6: `slice.mp4` contains at least one visual cut (measured by pixel difference between two frames extracted at different timestamps).
- C7: `verify.py` passes its own fault-proof check (detects failure on a corrupted artifact under scratch/).
