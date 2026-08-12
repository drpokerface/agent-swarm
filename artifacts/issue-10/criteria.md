# Criteria for Audio Production

## Interpretation
- We must generate all TTS dialogue audio files for the script 'script.json' using the strongest available APIs (Gemini 2.5 TTS or similar).
- We must procure or generate simple royalty-free sound effects (SFX) and background music (BGM) to ensure no dead air.
- All files must be in WAV or MP3 format and packaged into 'audio.zip' with a manifest JSON mapping files to script lines.
- We need to verify high audio quality, distinct character voices, and lack of silent gaps.

## Claims
C1: The file 'audio.zip' exists and is a valid zip archive containing 'manifest.json' and the generated audio files.
C2: 'manifest.json' correctly maps each dialogue/script item to its generated audio file.
C3: All dialogue files exist as valid non-empty WAV or MP3 files.
C4: Character voices are distinct and high-quality.
C5: BGM and SFX are present, non-empty, and can be used to fill dead air.
