# Plan
1. Parse `script.json` for assets.
2. Generate backgrounds and sprites using the working image model.
3. Remove backgrounds from sprites (transparency) if the model doesn't natively do it.
4. Package into `visuals.zip`.
5. Check visuals with a perceptual tool.
6. Fix any issues and run verify.py.

# Node Tree
C1: visuals.zip exists (RED)
C2: Backgrounds are 1280x720 (RED)
C3: Sprites have transparency (RED)
C4: Visual consistency (RED)
