# Plan
1. Understand spec and characters.
2. Write criteria.md and verify.py.
3. Generate audio files for each shot using TTS (OpenAI if available, else gTTS with pitch/speed modifications).
4. Trim silences using pydub.
5. Generate/find SFX/Music.
6. Create timeline.json.
7. Package to audio.zip.
8. Refine audio quality based on judge feedback.

# Node Tree
- C1 (audio.zip exists): red (turn 14)
- C2 (timeline.json covers all shots): red (turn 14)
- C3 (all referenced audio files exist): red (turn 14)
- C4 (silences trimmed): red (turn 14)
- C5 (SFX included): red (turn 14)
- C6 (distinct comedic voices): red (turn 14)

# Facts
F1 | TTS capabilities: OpenAI and gTTS are installed (turn 4).
F2 | 38 script items (turn 13).
