# System Capabilities and Probe Findings

## Image Generation
- **Models**: `gemini-2.5-flash` successfully returns inline `image/png` data when prompted for images.
- **API Limits**: Standard Gemini API limits apply (e.g. 15 RPM free, scaling higher on paid tier).

## Audio/TTS
- **Models**: `gemini-2.5-flash-preview-tts` and `gemini-2.5-pro-preview-tts` return raw audio.
- **API Limits**: Standard Gemini limits.

## Video Assembly
- **Tool**: `ffmpeg`
- **Capabilities**: Muxes generated images and audio into MP4 effectively.
- **Limits**: Constrained by local CPU.
