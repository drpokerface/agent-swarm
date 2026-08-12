Plan:
1. Read artifacts and inspect capabilities/scripts (Done, Turn 4)
2. Write criteria.md (Done, Turn 5)
3. Write verify.py (RED) (Done, Turn 5)
4. Generate TTS distinct voices for Brody, Karen, Sybil using OpenAI TTS (Turn 6+)
5. Trim dead air from TTS using pydub
6. Generate or fetch SFX/BGM
7. Generate timeline.json
8. Zip to audio.zip

Nodes:
- C1: audio.zip exists (RED)
- C2: timeline.json valid (RED)
- C3: Files exist (RED)
- C4: SFX/BGM exist (RED)
- C5: Trimmed audio (RED)
- C6: Distinct voices (RED)
