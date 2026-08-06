# Plan
1. [x] Parse script.json and verify all dialogue lines, timestamps, and audio cues.
2. [x] Research edge-tts or alternative TTS mechanisms.
3. [ ] Generate SFX and BGM.
4. [x] Build verify.py script to run checks first (RED state).
5. [ ] Synthesize all dialogue files and verify they match expectations.
6. [ ] Synthesize all BGM/SFX and verify.
7. [ ] Compress everything into audio.zip.
8. [ ] Run verify.py, resolve failures, and perform Fault-Proof test.
9. [ ] Pre-flight and declare "done".

# Node Tree
- C1: RED
- C2: RED
- C3: RED
- C4: RED
- C5: RED

# Facts
- F1 | Total scenes: 3 | Turn 8
- F2 | Dialogue lines: 18 (Dave: 7, Zalgor: 11) | Turn 8
- F3 | Cues: 7 (BGM/ambient: 2, SFX: 5) | Turn 8
- F4 | edge-tts is installed and working | Turn 24
- F5 | gTTS is installed and working | Turn 24
