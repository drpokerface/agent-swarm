## Interpretation
The goal requires a specialized constitution and rubric for an adult-animation comedy short. The style is explicitly "irreverent, fast-paced adult-animation comedy" akin to South Park and Family Guy.
- "No placeholders" means any "TODO", "Lorem ipsum", or explicit placeholder text is a failure.
- Word count > 500 across the two required files.
- Zip bundle must extract successfully and contain constitution.md and manifest.md.
- The threshold of 7 must be explicitly stated.

## Claims
C1: `constitution_bundle.zip` exists at the root.
C2: `constitution_bundle.zip` is a valid, decodable zip archive.
C3: The archive contains exactly `constitution.md` and `manifest.md` (and optional hidden system files).
C4: The combined text of `constitution.md` and `manifest.md` is strictly greater than 500 words.
C5: `constitution.md` contains explicit sections for "strategy", "style decisions", "conventions", and a "scoring rubric".
C6: The rubric explicitly anchors scores of 4, 7, and 9 for four dimensions: humor, pacing, visual cohesion, and audio sync, and explicitly sets a threshold of 7.
C7: `manifest.md` lists concrete filenames, formats, and includes a sample snippet proving the format.
C8: The text contains no degenerate patterns (e.g., uniform repetition) or placeholders (e.g., "TODO", "[Insert]").
C9: Subjective Quality: A fresh LLM judge scores the constitution against the rubric at >= 7 for overall utility and alignment with the required adult-animation style.
