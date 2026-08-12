Audio Generation & Processing

SHARED SPEC: The goal is an original ~2 minute animated comedy short (final.mp4, 1280x720) in an irreverent, satirical adult-animation style (e.g. Family Guy, South Park). Must include character voices, synced dialogue audio, music/sfx. Require a hook in the first 5 seconds, no dead air, and a punchline payoff at the end. Use cutout animation or similar. High quality bar for comedic timing and clear visuals.

Read `script.json` and use the audio tools identified in `capabilities.md`. Generate high-quality TTS audio for every line of dialogue, assigning distinct comedic voices to different characters. Generate or fetch appropriate sound effects and background music. Trim all dead air from the audio clips. Package all .wav/.mp3 files along with a `timeline.json` file that maps each audio file to its corresponding scene/shot in the script into a single archive named `audio.zip`. 

JUDGING CRITERIA: Passes if `audio.zip` can be extracted to reveal clear, distinct voice files for all script lines, SFX/music tracks, and a valid `timeline.json`. Audio must sound natural/comedic with zero unintended silences at the start/end of the clips.

Save the main deliverable as audio.zip.

Already provided in your working directory: artifacts/issue-13/spec.md, artifacts/issue-14/capabilities.md, artifacts/issue-15/script.json
