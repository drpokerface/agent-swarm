## Interpretation
The goal requires generating visual assets for an animated comedy short based on `script.json`.
1. Backgrounds: Every unique background described in `script.json` must have a corresponding 1280x720 PNG image.
2. Characters: Every unique character state (pose) described in `script.json` must have a corresponding transparent PNG image, with both "mouth_open" and "mouth_closed" variations.
3. Packaging: All images must be packaged into `visuals.zip`.
4. Style: Consistent irreverent, satirical adult-animation style (like Family Guy / South Park).

## Claims
- C1: `visuals.zip` exists in the workspace.
- C2: `visuals.zip` contains a 1280x720 `.png` file for every unique background in `script.json`.
- C3: `visuals.zip` contains transparent `.png` files for every unique character state in `script.json` (specifically `_mouth_open.png` and `_mouth_closed.png` for each).
