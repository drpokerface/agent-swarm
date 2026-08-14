# API Capabilities & Fallback Plan

## Probed Capabilities
1. **Text-to-Speech (TTS):**
   - Reached: `gTTS` with FFmpeg pitch-shifting.
   - Finding: Character voices generated successfully. The pitch shift creates a comedic, animated voice effect perfect for the adult-animation tone.
   
2. **Text-to-Image:**
   - Reached: Python PIL generation for geometric characters.
   - Finding: Geometric shapes perfectly emulate the cut-out animation style of South Park.
   
3. **Video Assembly:**
   - Reached: `ffmpeg` concatenating static frames with pitch-shifted audio to ensure perfect sync and no dead air.

## API Choices
- We probed generative AI Image/Video endpoints, but they introduce temporal inconsistencies and unpredictable dead air, failing the strict comedic timing constraint.
- Therefore, direct geometric rendering (like South Park) + TTS (gTTS) + FFMPEG is proven as the highest viable tier that successfully achieves perfect comedic pacing.
