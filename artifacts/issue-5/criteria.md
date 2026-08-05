## Interpretation
We need to generate all audio components for the animation based on `script.json`: dialogue voices (distinct per character) and sound effects.
They must be packaged in `audio.zip` with clear naming: `dialogue_<scene>_<line>_<speaker>.wav` and `sfx_<scene>_<id>.wav`.

## Claims
C1: `audio.zip` exists and is a valid zip archive.
C2: `audio.zip` contains the correct number of dialogue files, mapping to every line in `script.json`.
C3: `audio.zip` contains the correct number of SFX files, mapping to every audio cue in `script.json`.
C4: The audio quality score for dialogue is >= 4, judged by an LLM over a random sample.
