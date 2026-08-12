## Interpretation
The goal is to generate audio assets for an animated comedy short based on `script.json`. The deliverable is `audio.zip`.
The zip must contain:
- Audio files (TTS for dialogue, plus SFX/music).
- `timeline.json` mapping each audio file to its script index.
- All TTS files must be trimmed of starting and ending silence.
- Different characters must have distinct voices.

C1: `audio.zip` exists and is a valid zip archive.
C2: `timeline.json` is present in the root of `audio.zip`.
C3: `timeline.json` covers all shots from `script.json` and maps them to valid audio files present in the zip.
C4: The referenced dialogue audio files are trimmed (no significant leading/trailing silence).
C5: At least one SFX or background music track is present in the zip.
