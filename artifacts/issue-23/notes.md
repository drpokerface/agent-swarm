Plan:
1. Initialize criteria.md and notes.md.
2. Write and run verify.py RED.
3. Extract assets.zip, read script.json, check constitution.md.
4. Build Rough Cut (audio + visual assets) script-driven.
5. Polish loop (judge and refine: fix dead air, sync, effects).
6. Final packaging and verify.py GREEN.

Degenerate Twins:
- D1: A silent 120s 1280x720 black video.
- D2: A video with static white noise and no real audio or visuals.
- D3: A single frame held for 120s with a single drone sound.
- D4: A video assembled without using script.json or assets.zip.

Node Tree:
- root: final.mp4 meets all criteria [assumed]
  - C1: exists [assumed]
  - C2: streams (video+audio) [assumed]
  - C3: 1280x720 [assumed]
  - C4: 100-140s duration [assumed]
  - C5: non-degenerate [assumed]
  - C6: subjective score >= 7 [assumed]
