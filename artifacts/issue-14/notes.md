# Plan
1. Write criteria.md and verify.py (RED)
2. Probe environment for TTS (gTTS, OpenAI, ElevenLabs, etc.)
3. Probe environment for Image Gen (DALL-E, Stable Diffusion, etc.)
4. Probe environment for Video Assembly (moviepy, ffmpeg)
5. Document findings in capabilities.md
6. Generate images for slice.mp4
7. Generate audio for slice.mp4
8. Assemble slice.mp4 using moviepy (10s, 1 cut, 1 voiced line)
9. Run verify.py (GREEN)

# Node Tree
- root: red (no artifacts)
  - C1 (Capabilities): red
  - C2 (Video Format): red
  - C3 (Audio Format): red
  - C4 (Video Length): red
  - C5 (Visual Cut): red
  - C6 (Quality Baseline): red

# Facts
