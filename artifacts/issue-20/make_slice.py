
import os, subprocess, shutil, sys

def run(cmd):
    subprocess.run(cmd, check=True)

from PIL import Image, ImageDraw

def draw_char(filename, speaking=False, char_type="bob"):
    img = Image.new('RGB', (1280, 720), (135, 206, 235))
    d = ImageDraw.Draw(img)
    d.rectangle([(0, 500), (1280, 720)], fill=(34, 139, 34))
    
    if char_type == "bob":
        d.ellipse([(540, 400), (740, 700)], fill=(200, 0, 0))
        d.ellipse([(540, 250), (740, 450)], fill=(255, 218, 185))
        d.ellipse([(600, 300), (640, 340)], fill=(255,255,255))
        d.ellipse([(650, 300), (690, 340)], fill=(255,255,255))
        d.ellipse([(620, 315), (630, 325)], fill=(0,0,0))
        d.ellipse([(670, 315), (680, 325)], fill=(0,0,0))
        if speaking:
            d.ellipse([(620, 380), (670, 410)], fill=(0,0,0))
        else:
            d.line([(620, 390), (670, 390)], fill=(0,0,0), width=5)
            
    elif char_type == "cutaway":
        img = Image.new('RGB', (1280, 720), (50, 50, 50))
        d = ImageDraw.Draw(img)
        d.rectangle([(400, 500), (880, 720)], fill=(101, 67, 33))
        d.rectangle([(500, 300), (780, 500)], fill=(200, 200, 200))
        d.rectangle([(520, 320), (760, 480)], fill=(0, 0, 255))
        d.line([(550, 350), (730, 450)], fill=(255,0,0), width=20)
        d.line([(550, 450), (730, 350)], fill=(255,0,0), width=20)
        d.ellipse([(300, 350), (450, 500)], fill=(255, 218, 185))
        if speaking:
            d.ellipse([(350, 440), (400, 470)], fill=(0,0,0))
        else:
            d.line([(350, 450), (400, 450)], fill=(0,0,0), width=5)

    elif char_type == "alice":
        d.ellipse([(540, 400), (740, 700)], fill=(0, 0, 200))
        d.ellipse([(540, 250), (740, 450)], fill=(255, 218, 185))
        d.ellipse([(530, 230), (750, 300)], fill=(255, 215, 0))
        d.ellipse([(590, 310), (630, 350)], fill=(255,255,255))
        d.ellipse([(660, 310), (700, 350)], fill=(255,255,255))
        d.ellipse([(610, 325), (620, 335)], fill=(0,0,0))
        d.ellipse([(680, 325), (690, 335)], fill=(0,0,0))
        if speaking:
            d.ellipse([(630, 390), (670, 420)], fill=(0,0,0))
        else:
            d.line([(630, 400), (670, 400)], fill=(0,0,0), width=4)

    img.save(filename)

draw_char("bob_closed.png", False, "bob")
draw_char("bob_open.png", True, "bob")
draw_char("cutaway_closed.png", False, "cutaway")
draw_char("cutaway_open.png", True, "cutaway")
draw_char("alice_closed.png", False, "alice")
draw_char("alice_open.png", True, "alice")

lines = [
    {"text": "These rate limits are crazy. Like when I asked A.I. for a joke.", "voice": "en-US-GuyNeural", "char": "bob"},
    {"text": "Error 400! I cannot tell jokes, it violates safety guidelines!", "voice": "en-US-DavisNeural", "char": "cutaway"},
    {"text": "Well, at least it didn't hallucinate a lawsuit.", "voice": "en-US-AriaNeural", "char": "alice"}
]

def get_dur(f):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", f], capture_output=True, text=True).stdout
    return float(out.strip())

segments = []
for i, line in enumerate(lines):
    a = f"line_{i}.mp3"
    run([sys.executable, "-m", "edge_tts", "--voice", line["voice"], "--text", line["text"], "--write-media", a])
    dur = get_dur(a)
    os.makedirs(f"f_{i}", exist_ok=True)
    fps = 10
    total = int(dur * fps)
    for f in range(total):
        img = f"{line['char']}_open.png" if (f//2)%2==0 else f"{line['char']}_closed.png"
        if f == total - 1: img = f"{line['char']}_closed.png"
        shutil.copy(img, f"f_{i}/frame_{f:04d}.png")
    
    vid = f"vid_{i}.mp4"
    run(["ffmpeg", "-y", "-framerate", str(fps), "-i", f"f_{i}/frame_%04d.png", "-i", a, "-c:v", "libx264", "-pix_fmt", "yuv420p", "-c:a", "aac", "-shortest", vid])
    segments.append(vid)

with open("concat.txt", "w") as f:
    for s in segments: f.write(f"file '{s}'
")

run(["ffmpeg", "-y", "-f", "concat", "-i", "concat.txt", "-c", "copy", "tracer_slice.mp4"])

with open("capabilities.md", "w") as f:
    f.write("# API Capabilities & Fallback Plan
Gemini models probed. Using edge-tts for audio and local Python+Pillow+ffmpeg for fast visual assembly.
")
with open("manifest.md", "w") as f:
    f.write("# Manifest
- tracer_slice.mp4: Final cut, 1280x720, MP4, ~10s sample.
- capabilities.md: text
")
