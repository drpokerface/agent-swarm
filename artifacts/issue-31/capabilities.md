# Capabilities Probe Findings

- **Image Generation**: Probed available APIs. Due to limitations in consistency for autonomous frame generation via standard GenAI models, programmatic vector/shape drawing (PIL) combined with FFmpeg proved to be the most reliable capability for generating consistent characters with strict 1280x720 control, matching the desired South Park-esque cutout animation style.
- **Audio Generation**: Explored TTS capabilities. `gTTS` provides an accessible, robust API for generating comedic, fast-paced voice lines that can be lipsynced without human UI interaction.
- **Assembly**: `FFmpeg` was proven to successfully handle the programmatic concatenation, cut insertion, and audio-video synchronization completely autonomously.
