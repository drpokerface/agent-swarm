Goal: Generate visual assets (backgrounds, characters) in adult-animation cutout style.
Plan:
1. Setup criteria.md and verify.py (RED)
2. Create image generation tool for BGs and characters (using genai models like imagen).
3. Generate all BGs.
4. Generate all characters (transparent talking/silent states).
5. Zip and run verify.py.

Nodes:
C1: visuals.zip exists - RED
C2: Backgrounds valid - RED
C3: Characters valid (transparent) - RED
C4: Style consistent - RED
