## Interpretation
The goal is to generate visual assets for a 2-minute cutout animation comedy short.
The assets must be packaged in `visuals.zip`.
The zip will have the following structure:
- `backgrounds/<md5_of_background_string>.png` : All 1280x720, opaque.
- `characters/<CharacterName>_silent.png` : With alpha channel (transparent).
- `characters/<CharacterName>_talking.png` : With alpha channel.
The required characters are Brody, Karen, and Sybil.

## Claims
C1: `visuals.zip` exists and is a valid zip file.
C2: For every unique `background` in `artifacts/issue-15/script.json`, a corresponding 1280x720 PNG exists in `visuals.zip` under the `backgrounds/` folder.
C3: For Brody, Karen, and Sybil, both a `_silent.png` and `_talking.png` exist in `visuals.zip` under the `characters/` folder, and they possess an alpha channel.
C4: The generated visual assets are confirmed by a fresh LLM call to match the adult-animation cutout style.
