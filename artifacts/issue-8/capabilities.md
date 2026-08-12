# Capabilities Probe Findings

## Image Generation
Probed GenAI SDK `generate_images` with models like `imagen-3.0-generate-002`. Failed.
Fallback: PIL primitives (Allowed by spec since no better tier reachable).

## TTS Audio
Probed `edge-tts`. Successful. Using `en-US-AriaNeural` and `en-US-GuyNeural`.

## Video Assembly
Using `ffmpeg` via `imageio-ffmpeg`.

## API Limits
- Gemini API reachable for text/models listing, image generation blocked.
- Edge-TTS has no hard limit.
