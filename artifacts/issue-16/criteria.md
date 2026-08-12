## Interpretation
We need to generate high-quality audio for each line of dialogue in artifacts/issue-15/script.json.
Each character gets a distinct voice. We use edge-tts to generate English voices.
We must also provide/generate SFX and background music tracks.
All clips must be trimmed of dead air (unintended silence at the start/end).
We package all .wav/.mp3 files along with a timeline.json file mapping each audio file to its corresponding scene/shot in the script into a single archive named audio.zip.

## Claims
- C1: audio.zip is a valid zip archive in the workspace root.
- C2: Extracting audio.zip contains a valid timeline.json mapping every dialogue line to its audio file, scene index, sfx, and music.
- C3: All referenced audio files in timeline.json exist inside the extracted folder of audio.zip.
- C4: The dialogue files have distinct, clear voice assignments for each character (Karen, Brody, Sybil).
- C5: All audio files (voices, sfx, bgm) are valid audio files and have been trimmed of dead air.
- C6: SFX and background music files are present in the timeline or archive.
