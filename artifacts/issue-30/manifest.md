# Manifest - Deliverable Files and Formats

This manifest defines the exact filenames and formatting requirements for all deliverables associated with the adult animation comedy short project.

## Deliverables

1. **constitution.md**
   - Format: Markdown text file.
   - Purpose: Contains the overarching philosophy, strategy, style decisions, conventions, and the detailed scoring rubric for evaluating project outputs.
   - Encoding: UTF-8.

2. **manifest.md**
   - Format: Markdown text file.
   - Purpose: Specifies file naming structures, formatting guidelines, and provides an executable sample of the expected output.
   - Encoding: UTF-8.

## Tiny Sample Proving Format
The following is a small scene screenplay representing a 5-second punchy animation sequence matching the adult comedy style. It demonstrates the precise formatting required for script deliverables, ensuring fast-paced dialogue and clear visual directions.

```json
{
  "sequence_id": "SCN_01_AWKWARD_DINNER",
  "duration_seconds": 5.0,
  "characters": ["JIM", "ALIEN_BOB"],
  "actions": [
    {
      "timecode": "00:00:00.00",
      "type": "visual",
      "description": "Wide shot, 1280x720. Jim and Alien Bob sit at a small, poorly lit kitchen table. A single bowl of grey mush sits between them."
    },
    {
      "timecode": "00:00:01.00",
      "type": "audio",
      "character": "JIM",
      "dialogue": "So. The invasion.",
      "delivery": "Deadpan, exhausted."
    },
    {
      "timecode": "00:00:02.50",
      "type": "visual",
      "description": "Quick zoom in on Alien Bob's face. His multiple eyes blink asynchronously."
    },
    {
      "timecode": "00:00:03.00",
      "type": "audio",
      "character": "ALIEN_BOB",
      "dialogue": "We are rethinking it. Your cholesterol levels are horrifying.",
      "delivery": "Matter-of-fact, slightly disgusted."
    },
    {
      "timecode": "00:00:05.00",
      "type": "visual",
      "description": "Smash cut to black."
    }
  ]
}
```
This sample proves the format requires explicit timecodes, visual cues tailored for a 1280x720 canvas, and punchy, irreverent dialogue characteristic of our target style.
