# Script Manifest

**Output file:** `script.json`
**Format:** JSON

## Schema
The file contains a JSON array of scene objects. Each scene object MUST contain the following properties:

- `dialogue` (string): The exact spoken lines for the scene, including character names.
- `visual_prompt` (string): Detailed description of the action and visual setting for image generation.
- `duration` (number): Estimated time in seconds the scene will take (can be mapped to `estimated_duration`).
- `estimated_duration` (number): Equivalent to duration, used for time tracking.
- `tts_profiles` (array of strings): The list of character voices required for the scene.

## Sample
```json
[
  {
    "dialogue": "Xylar: Zorblax, look at this! Earth's digital footprint is a localized brain rot so powerful it’s collapsing the Andromeda star system! We have to blow it up!",
    "visual_prompt": "Inside a high-tech alien spaceship cockpit. Xylar, a green, three-eyed alien with an oversized brain, gestures frantically.",
    "duration": 20.0,
    "estimated_duration": 20.0,
    "tts_profiles": ["Xylar"]
  }
]
```
