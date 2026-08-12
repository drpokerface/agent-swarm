## Interpretation
The goal is to produce all dialogue audio lines via TTS, and gather/generate BGM and SFX for an adult animated comedy short. The audio must be clear, distinct for each character, and packaged into `audio.zip` containing all audio files (WAV or MP3) and a `manifest.json`.

## Claims
1. **C1 (Zip Exists):** `audio.zip` exists in the workspace root and is a valid zip archive.
2. **C2 (Manifest Exists):** `audio.zip` contains a file named `manifest.json` at its root.
3. **C3 (Completeness):** `manifest.json` contains a `dialogue` list with exactly one entry for each line in `artifacts/issue-9/script.json`, plus `bgm` and `sfx` fields.
4. **C4 (Audio Validity):** Every file referenced in `manifest.json` exists in `audio.zip` and is a valid audio file with >0s duration (verified via ffprobe).
