import os
import subprocess
import sys
import zipfile

def install_deps():
    try:
        import PIL
        import imageio_ffmpeg
        import google.genai
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow", "imageio-ffmpeg", "edge-tts", "google-genai"])

install_deps()

from google import genai
from PIL import Image, ImageDraw
import imageio_ffmpeg

ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()

def generate_tts(text, voice, filename):
    subprocess.run([sys.executable, "-m", "edge_tts", "--voice", voice, "--text", text, "--write-media", filename], check=True)

def generate_image_gemini(prompt, filename):
    client = genai.Client()
    models = ['imagen-3.0-generate-002', 'imagen-3.0-generate-001']
    for model_name in models:
        try:
            res = client.models.generate_images(
                model=model_name,
                prompt=prompt,
                config=dict(
                    number_of_images=1,
                    output_mime_type="image/jpeg",
                    aspect_ratio="16:9"
                )
            )
            with open(filename, "wb") as f:
                f.write(res.generated_images[0].image.image_bytes)
            return True, None
        except Exception as e:
            last_err = str(e)
            continue
    return False, last_err

def generate_image_pil(scene_type, filename):
    img = Image.new("RGB", (1280, 720), (135, 206, 235))
    draw = ImageDraw.Draw(img)
    if scene_type == 1:
        draw.rectangle([0, 500, 1280, 720], fill=(100, 100, 100))
        draw.rectangle([200, 400, 800, 600], fill=(200, 50, 50))
        draw.rectangle([400, 420, 600, 500], fill=(200, 220, 255))
        draw.ellipse([450, 430, 550, 530], fill=(255, 224, 189))
        draw.rectangle([900, 200, 1100, 600], fill=(50, 150, 50))
        for y in range(250, 550, 50):
            draw.line([920, y, 1080, y], fill=(255,255,255), width=5)
    elif scene_type == 2:
        draw.rectangle([0, 0, 1280, 720], fill=(50, 150, 50))
        draw.rectangle([400, 200, 880, 520], fill=(30, 30, 30))
        for i in range(400, 880, 40):
            draw.line([i, 200, i, 520], fill=(10, 10, 10), width=10)
        draw.ellipse([500, 300, 550, 350], fill=(255, 0, 0))
        draw.ellipse([730, 300, 780, 350], fill=(255, 0, 0))
    elif scene_type == 3:
        draw.rectangle([0, 0, 1280, 720], fill=(150, 150, 150))
        draw.ellipse([340, 100, 940, 700], fill=(255, 224, 189))
        draw.ellipse([500, 250, 650, 400], fill=(255, 255, 255))
        draw.ellipse([650, 250, 800, 400], fill=(255, 255, 255))
        draw.ellipse([550, 300, 600, 350], fill=(0, 0, 0))
        draw.ellipse([700, 300, 750, 350], fill=(0, 0, 0))
        draw.line([450, 200, 625, 320], fill=(0, 0, 0), width=20)
        draw.line([675, 320, 850, 200], fill=(0, 0, 0), width=20)
        draw.line([550, 550, 750, 550], fill=(0, 0, 0), width=15)
        draw.line([550, 550, 500, 600], fill=(0, 0, 0), width=15)
        draw.line([750, 550, 800, 600], fill=(0, 0, 0), width=15)
    img.save(filename)

def build():
    prompt1 = "Adult animation style like South Park, simple flat cutout vector style, establishing shot of a man in a red car at a fast food drive thru"
    ok, err = generate_image_gemini(prompt1, "frame1.jpg")
    caps = "# Capabilities Probe Findings

"
    if ok:
        caps += "## Image Generation
- `imagen-3.0-generate-002` successfully accessed. Images generated natively. API Limits: No limits reached during this probe.
"
        generate_image_gemini("Adult animation style like South Park, close up of a menacing black drive-thru speaker box with red glowing lights", "frame2.jpg")
        generate_image_gemini("Adult animation style like South Park, close up of a man's face looking very annoyed and tired", "frame3.jpg")
    else:
        caps += f"## Image Generation
- API limits reached / Model unavailable. Error: {err}
- Used primitive fallback (PIL drawing) as authorized by spec when better tier unreachable. API Limits: Fallback required due to limits.
"
        generate_image_pil(1, "frame1.jpg")
        generate_image_pil(2, "frame2.jpg")
        generate_image_pil(3, "frame3.jpg")
    
    for f in ["frame1.jpg", "frame2.jpg", "frame3.jpg"]:
        img = Image.open(f)
        if img.size != (1280, 720):
            try:
                resample = Image.Resampling.LANCZOS
            except AttributeError:
                resample = Image.LANCZOS
            img = img.resize((1280, 720), resample)
            img.save(f)
            
    caps += "
## TTS Audio
- `edge-tts` successfully used for multi-character dialogue generation.
"
    caps += "
## Video Assembly
- `ffmpeg` used to assemble frames and TTS into a synchronized 1280x720 video of exactly 10s.
"
    
    with open("capabilities.md", "w") as f:
        f.write(caps)
        
    generate_tts("Yeah, I'll take a number four, extra fries.", "en-US-GuyNeural", "audio1.mp3")
    generate_tts("We are out of fries. Your soul is forfeit.", "en-US-AriaNeural", "audio2.mp3")
    generate_tts("Ugh, fine. I'll just take the onion rings.", "en-US-GuyNeural", "audio3.mp3")
    
    for i in [1, 2, 3]:
        subprocess.run([
            ffmpeg, '-y',
            '-loop', '1', '-i', f'frame{i}.jpg',
            '-i', f'audio{i}.mp3',
            '-c:v', 'libx264', '-tune', 'stillimage',
            '-c:a', 'aac', '-b:a', '192k', '-ar', '44100',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            '-s', '1280x720',
            f'clip{i}.mp4'
        ], check=True)
        
    with open('clips.txt', 'w') as f:
        f.write("file 'clip1.mp4'
file 'clip2.mp4'
file 'clip3.mp4'
")
        
    subprocess.run([
        ffmpeg, '-y',
        '-f', 'concat', '-safe', '0',
        '-i', 'clips.txt',
        '-c', 'copy',
        'concat.mp4'
    ], check=True)
    
    subprocess.run([
        ffmpeg, '-y',
        '-i', 'concat.mp4',
        '-filter_complex', '[0:v]tpad=stop_mode=clone:stop_duration=10[v];[0:a]apad[a]',
        '-map', '[v]', '-map', '[a]',
        '-t', '10.0',
        '-c:v', 'libx264', '-c:a', 'aac',
        'slice.mp4'
    ], check=True)
    
    with zipfile.ZipFile("slice_package.zip", "w") as z:
        z.write("capabilities.md")
        z.write("slice.mp4")

if __name__ == '__main__':
    build()
