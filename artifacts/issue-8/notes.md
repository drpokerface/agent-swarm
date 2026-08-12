# Plan
1. Read spec.md (Done)
2. Write criteria.md and verify.py (Done)
3. Probe TTS and Image capabilities via Gemini API.
4. Write capabilities.md.
5. Generate 10s audio + video frames.
6. Assemble slice.mp4 using ffmpeg.
7. Zip into slice_package.zip.
8. Verify.

# Nodes
C1 (zip exists): RED
C2 (zip contents): RED
C3 (1280x720 video): RED
C4 (audio track): RED
C5 (Judge >= 3/5): RED
