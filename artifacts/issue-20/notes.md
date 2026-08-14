# Plan
1. Define criteria.md based on constitution.md and goal. (Done - turn 2)
2. Write verify.py (RED) matching criteria, including a fault-proof. (Turn 2-3)
3. Complete capabilities.md based on API probe. (Turn 2-3)
4. Build end-to-end tracer_slice.mp4. (Turn 4+)
5. Write manifest.md. (Turn 4+)
6. Improve quality (climb ladder) to pass subjective threshold (>7).

# Degenerate Twins
- **The Empty Twin**: files exist but are empty or 0 bytes.
- **The Blank/Silent Twin**: video file exists and is 1280x720, but consists of pure black/white screen and complete silence.
- **The Off-spec Twin**: video exists, but is missing audio tracks, or has incorrect resolution (not 1280x720), or duration is wrong (<5s or >15s).
- **The Boring Twin**: video and audio are present, but it's just static text and a plain beep or robotic TTS reading dry sentences, failing the adult-animation / comedy style.
- **The Manifest Disconnect Twin**: manifest exists but has mismatched files or formats, or lacks sample description.

# Node Tree
- Root: Tracer Slice & Capability Probe [assumed]
  - C1: tracer_slice.mp4 exists, 1280x720, 5-15s, has audio and video tracks [assumed]
  - C2: capabilities.md exists and contains accurate API capability findings [assumed]
  - C3: manifest.md exists, lists all required files/formats/samples [assumed]
  - C4: tracer_slice.mp4 is non-degenerate (non-blank, non-silent) [assumed]
  - C5: Perceptual score >= 7 against the adult animation rubric [assumed]

# Facts
- F1 | Gemini models list includes gemini-2.5-flash-preview-tts and gemini-2.5-flash-image | evidence: turn 1 [verified]
