## Interpretation
"
"The goal is to generate an audio package for the animation script, saved as `audio.zip`.
"
"This audio package must contain dialogue audio files for each character in the script, and SFX/Music files as specified by the cues.
"
"Characters DAVE and ZALGOR must have distinct, appropriate, and high-quality voices.
"
"
"
"### Named Claims
"
"C1: `audio.zip` exists in the root of the workspace.
"
"C2: `audio.zip` is a valid zip file containing all required folders/files.
"
"C3: All dialogue lines from script.json have corresponding audio files in the zip under a standardized naming convention (e.g., `scene_<id>_dialogue_<idx>_<speaker>.mp3`).
"
"C4: All audio cues (SFX and Music) from script.json have corresponding audio files in the zip under a standardized naming convention (e.g., `scene_<id>_cue_<idx>_<type>_<slug>.mp3`).
"
"C5: Dialogue files for different speakers have distinct voice signatures, validated by a perceptual test.
"
"C6: Every audio file is a valid, playable audio file of non-zero duration.
"
"C7: The total generated audio files match the content of the script with high quality (average audio quality score >= 4.0/5.0 as assessed by a model judge).
"
