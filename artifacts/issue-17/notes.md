# Plan
1. Analyze script.json, capabilities.md, spec.md
2. Refine criteria.md and verify.py based on exact schema of script.json (including fault-proofs)
3. Implement image generation pipeline using capabilities.md
4. Generate backgrounds (1280x720)
5. Generate characters (transparent PNGs, open/closed mouth)
6. Judge style consistency
7. Package visuals.zip

# Node Tree
- C1 (visuals.zip exists): red
- C2 (backgrounds exist & 1280x720): red
- C3 (character mouth states & transparency): red
- C4 (visual style is consistent): red

# Facts
