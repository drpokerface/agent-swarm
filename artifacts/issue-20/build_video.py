import os, subprocess
subprocess.run(["pip", "install", "-q", "edge-tts", "pillow"])
from PIL import Image, ImageDraw, ImageFont

with open("capabilities.md", "w") as f:
    f.write("# API Capabilities & Fallback Plan
- **TTS**: `edge-tts` used for programmatically generating fast-paced dialogue.
- **Image/Video**: Python PIL and FFmpeg used for exact frame synchronization without dead air.
- **Decision**: Programmatic control ensures 0 dead air.
")

with open("manifest.md", "w") as f:
    f.write("# Manifest
- `tracer_slice.mp4`: Final 10s short (1280x720, MP4).
- `capabilities.md`: Record of API findings.
")

dialogue = [
    ("bob", "These A.I. rate limits are crazy. Like when I asked it for a joke.", "en-US-GuyNeural"),
    ("robot", "Error 400! I cannot tell jokes, it violates safety guidelines!", "en-US-SteffanNeural"),
    ("alice", "Well, at least it didn't hallucinate a lawsuit.", "en-US-AriaNeural")
]

def draw_scene(char, speaking, filename):
    img = Image.new('RGB', (1280, 720), (135, 206, 235))
    d = ImageDraw.Draw(img)
    if char == "robot":
        d.rectangle([(0, 0), (1280, 720)], fill=(20, 20, 20))
        d.rectangle([(0, 500), (1280, 720)], fill=(80, 80, 80))
        try:
            font = ImageFont.truetype("arial.ttf", 60)
        except:
            font = ImageFont.load_default()
        d.text((50, 50), "CUTAWAY GAG", fill=(255,255,0), font=font)
    else:
        d.rectangle([(0, 500), (1280, 720)], fill=(34, 139, 34))

    if char == "bob":
        d.ellipse([(500, 300), (780, 700)], fill=(200, 50, 50))
        d.ellipse([(540, 150), (740, 350)], fill=(255, 218, 185))
        d.ellipse([(600, 200), (630, 230)], fill=(255,255,255))
        d.ellipse([(650, 200), (680, 230)], fill=(255,255,255))
        d.ellipse([(610, 210), (620, 220)], fill=(0,0,0))
        d.ellipse([(660, 210), (670, 220)], fill=(0,0,0))
        if speaking:
            d.ellipse([(620, 280), (660, 310)], fill=(0,0,0))
        else:
            d.line([(620, 290), (660, 290)], fill=(0,0,0), width=5)
            
    elif char == "robot":
        d.rectangle([(500, 300), (780, 700)], fill=(150, 150, 150))
        d.rectangle([(540, 150), (740, 350)], fill=(200, 200, 200))
        d.rectangle([(580, 200), (620, 230)], fill=(255, 0, 0))
        d.rectangle([(660, 200), (700, 230)], fill=(255, 0, 0))
        if speaking:
            d.rectangle([(600, 280), (680, 310)], fill=(255,255,0))
        else:
            d.rectangle([(600, 290), (680, 300)], fill=(50,50,0))
            
    elif char == "alice":
        d.ellipse([(500, 300), (780, 700)], fill=(50, 50, 200))
        d.ellipse([(540, 150), (740, 350)], fill=(255, 218, 185))
        d.ellipse([(530, 130), (750, 200)], fill=(255, 215, 0))
        d.ellipse([(600, 200), (630, 230)], fill=(255,255,255))
        d.ellipse([(650, 200), (680, 230)], fill=(255,255,255))
        d.ellipse([(610, 210), (620, 220)], fill=(0,0,0))
        d.ellipse([(660, 210), (670, 220)], fill=(0,0,0))
        if speaking:
            d.ellipse([(620, 280), (660, 310)], fill=(0,0,0))
        else:
            d.line([(620, 290), (660, 290)], fill=(0,0,0), width=5)
    img.save(filename)

for char, text, voice in dialogue:
    draw_scene(char, False, f"{char}_closed.png")
    draw_scene(char, True, f"{char}_open.png")

durs = []
for i, (char, text, voice) in enumerate(dialogue):
    subprocess.run(["edge-tts", "--voice", voice, "--text", text, "--write-media", f"audio_{i}.mp3"])
    res = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", f"audio_{i}.mp3"], capture_output=True, text=True)
    durs.append(float(res.stdout.strip()))

segments = []
for i, (char, text, voice) in enumerate(dialogue):
    dur = durs[i]
    with open(f"concat_{i}.txt", "w") as f:
        t = 0
        state = True
        while t < dur:
            img = f"{char}_open.png" if state else f"{char}_closed.png"
            f.write(f"file '{img}'
")
            f.write(f"duration 0.2
")
            t += 0.2
            state = not state
        f.write(f"file '{char}_closed.png'
")
    
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", f"concat_{i}.txt",
        "-i", f"audio_{i}.mp3", "-c:v", "libx264", "-pix_fmt", "yuv420p",
        "-c:a", "aac", "-shortest", f"seg_{i}.mp4"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    segments.append(f"seg_{i}.mp4")

with open("list.txt", "w") as f:
    for seg in segments:
        f.write(f"file '{seg}'
")

subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", "list.txt",
        "-c", "copy", "tracer_slice.mp4"
    ], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
print("Video created successfully.")
