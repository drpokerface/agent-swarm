## Interpretation
The goal is to generate and package audio for a comedy short based on `script.json`.
The deliverable is `audio.zip`, which contains all audio tracks and a `timeline.json` mapping them to the script.

## Claims
- C1: `audio.zip` exists in the workspace root.
- C2: `timeline.json` exists inside `audio.zip` and is a valid JSON array with length matching `script.json`.
- C3: Every file referenced in `timeline.json` (`dialogue_audio`, elements of `sfx_audio`, and `bgm_audio`) exists inside `audio.zip`.
- C4: The timeline references at least one SFX file and at least one BGM file across the scenes.
- C5: Dialogue audio files are trimmed, possessing less than 150ms of silence at the beginning and end (silence defined as < -40dBFS).
- C6: Distinct voices are used. The median pitches of Brody, Karen, and Sybil's dialogue files differ significantly (at least 5Hz difference between their averages).