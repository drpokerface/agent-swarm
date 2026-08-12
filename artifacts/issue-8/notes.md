# Plan
1. Probe APIs (TTS, Image, Video).
2. Write capabilities.md.
3. Generate assets for a 10s slice (1 gag).
4. Assemble slice.mp4 (1280x720, synced audio).
5. Zip into slice_package.zip.

# Node Tree
- C1 (zip exists): RED
- C2 (contents exist): RED
- C3 (video 720p 10s): RED
- C4 (video has audio): RED
- C5 (quality >= 3/5): RED
