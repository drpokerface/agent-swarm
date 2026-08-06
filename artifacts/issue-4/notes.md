# Notes

## Plan
1. Read spec.md and script.json to find required assets. (Turn 60) - DONE
2. Write criteria.md and verify.py. (Turn 60) - DONE
3. Run verify.py to see it fail (RED). (Turn 61) - DONE
4. Develop the asset generation script using PIL. (Turn 80) - DONE
5. Package into visuals.zip. (Turn 80) - DONE
6. Implement complete verify.py with robust fault-proof. (Turn 80) - DONE
7. Test and run verification to confirm everything is green. (Turn 80) - DONE

## Node Tree
- Root: Generate Visual Assets (green, turn 80)
  - C1: visuals.zip exists (green, turn 80)
  - C2: Backgrounds are 1280x720 (green, turn 80)
  - C3: Characters are RGBA transparent (green, turn 80)
  - C4: Visual gags/cutaways assets exist (green, turn 80)
  - C5: Style score >= 4/5 (green, turn 80)

## Facts
- F1 | Visual assets correctly cover all characters and backgrounds in the script | evidence: turn 80
- F2 | Characters are in transparent RGBA format with multiple mouth shapes for lip-syncing | evidence: turn 80
