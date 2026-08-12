## Interpretation
The goal requires generating visual assets (backgrounds and character cutouts) for an adult-animation comedy short and packaging them in `visuals.zip`.
- Backgrounds: Extract all unique `background` scenes from `script.json`. We need a 1280x720 PNG per unique background in a `backgrounds/` directory.
- Characters: Characters (Karen, Brody, Sybil) must each have a `talking.png` and `silent.png` in a `characters/<name>/` directory. These must be transparent PNGs to be used as cutouts.
- Style: The style must be highly consistent, irreverent, satirical adult-animation cutout style, evaluated by a perceptual judge.

## Claims
C1: `visuals.zip` exists.
C2: `visuals.zip` contains a `backgrounds/` folder with exactly one 1280x720 PNG image per unique background specified in `script.json`.
C3: `visuals.zip` contains a `characters/` folder with subfolders for each character containing at least `talking.png` and `silent.png`, which are transparent PNGs.
C4: The visual style is highly consistent across backgrounds and characters, matching the irreverent, satirical adult-animation cutout style.
