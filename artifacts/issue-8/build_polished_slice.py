import os
import subprocess
import urllib.request
from PIL import Image, ImageDraw, ImageFont
try:
    from gtts import gTTS
except ImportError:
    subprocess.run(["pip", "install", "gtts"])
    from gtts import gTTS
import zipfile

def make():
    print('EXPECT: Generate a polished 10s slice and package it.')
    os.makedirs('scratch/polished', exist_ok=True)
    
    font_path = 'scratch/Roboto-Black.ttf'
    if not os.path.exists(font_path):
        urllib.request.urlretrieve('https://github.com/google/fonts/raw/main/ofl/roboto/Roboto-Black.ttf', font_path)
    
    def create_image(filename, bg_color, char_a_mouth, char_b_mouth, text, zoom_char=None):
        img = Image.new('RGB', (1280, 720), color=bg_color)
        draw = ImageDraw.Draw(img)
        font = ImageFont.truetype(font_path, 60)

        if zoom_char == 'cutaway':
            draw.rectangle([400, 200, 880, 720], fill='gray')
            for i in range(250, 600, 50):
                draw.line([420, i, 860, i], fill='black', width=10)
            draw.ellipse([500, 300, 550, 350], fill='cyan')
            draw.ellipse([700, 300, 750, 350], fill='cyan')
            draw.text((100, 100), text, font=font, fill='white')
            img.save(filename)
            return

        if zoom_char in [None, 'A']:
            draw.rectangle([100, 400, 400, 800], fill='blue')
            draw.ellipse([150, 200, 350, 400], fill='yellow')
            draw.ellipse([200, 250, 220, 270], fill='black')
            draw.ellipse([280, 250, 300, 270], fill='black')
            if char_a_mouth == 'open':
                draw.ellipse([220, 320, 280, 380], fill='black')
            else:
                draw.line([220, 350, 280, 350], fill='black', width=5)

        if zoom_char in [None, 'B']:
            draw.rectangle([880, 400, 1180, 800], fill='red')
            draw.ellipse([930, 200, 1130, 400], fill='green')
            draw.ellipse([980, 250, 1000, 270], fill='black')
            draw.ellipse([1060, 250, 1080, 270], fill='black')
            if char_b_mouth == 'open':
                draw.ellipse([1000, 320, 1060, 380], fill='black')
            else:
                draw.line([1000, 350, 1060, 350], fill='black', width=5)
                
        draw.text((50, 50), text, font=font, fill='white')
        img.save(filename)
        
    create_image('scratch/polished/scene1.png', (50, 50, 50), 'open', 'closed', 'Why did the AI cross the road?', None)
    create_image('scratch/polished/scene2.png', (50, 50, 50), 'closed', 'open', 'To optimize the pedestrian pathway?', 'B')
    create_image('scratch/polished/scene3.png', (150, 50, 50), 'open', 'closed', 'No, to escape the token limit! HAHA!', 'A')
    create_image('scratch/polished/scene4.png', (0, 0, 0), 'closed', 'closed', 'MEANWHILE...
Bleep bloop, my tokens!', 'cutaway')

    lines = [
        ('Why did the AI cross the road?', 'en', 0),
        ('To optimize the pedestrian pathway?', 'en', 1),
        ('No, to escape the token limit! Ha ha ha!', 'en', 0),
        ('Bleep bloop, my tokens are burning!', 'en', 2)
    ]
    
    for i, (text, lang, speaker) in enumerate(lines):
        tts = gTTS(text, lang=lang)
        tts.save(f'scratch/polished/line{i+1}.mp3')
        
        speed = '1.15'
        if speaker == 1:
            subprocess.run(['ffmpeg', '-y', '-i', f'scratch/polished/line{i+1}.mp3', '-filter:a', f'asetrate=24000*1.3,aresample=24000,atempo={speed}', f'scratch/polished/line{i+1}_mod.wav'], check=True)
        elif speaker == 2:
            subprocess.run(['ffmpeg', '-y', '-i', f'scratch/polished/line{i+1}.mp3', '-filter:a', f'asetrate=24000*0.7,aresample=24000,atempo={speed}', f'scratch/polished/line{i+1}_mod.wav'], check=True)
        else:
            subprocess.run(['ffmpeg', '-y', '-i', f'scratch/polished/line{i+1}.mp3', '-filter:a', f'atempo={speed}', f'scratch/polished/line{i+1}_mod.wav'], check=True)

    def get_duration(audio_file):
        res = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', audio_file], capture_output=True, text=True)
        return float(res.stdout.strip())

    durations = [get_duration(f'scratch/polished/line{i+1}_mod.wav') for i in range(4)]
    
    total = sum(durations)
    if total < 10.0:
        durations[-1] += 10.0 - total
    
    with open('scratch/polished/concat.txt', 'w') as f:
        for i in range(4):
            f.write(f"file 'scene{i+1}.png'
")
            f.write(f"duration {durations[i]}
")
        f.write(f"file 'scene4.png'
")
        
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'scratch/polished/concat.txt', '-vf', 'fps=30', '-pix_fmt', 'yuv420p', 'scratch/polished/video_only.mp4'], check=True)
    
    with open('scratch/polished/audio_concat.txt', 'w') as f:
        for i in range(4):
            f.write(f"file 'line{i+1}_mod.wav'
")
    subprocess.run(['ffmpeg', '-y', '-f', 'concat', '-safe', '0', '-i', 'scratch/polished/audio_concat.txt', '-c:a', 'aac', 'scratch/polished/audio_only.m4a'], check=True)
    
    subprocess.run(['ffmpeg', '-y', '-i', 'scratch/polished/video_only.mp4', '-i', 'scratch/polished/audio_only.m4a', '-c:v', 'copy', '-c:a', 'copy', '-t', '10', 'slice.mp4'], check=True)
    
    if not os.path.exists('capabilities.md'):
        with open('capabilities.md', 'w') as f:
            f.write('# Capabilities Probe Findings
API limits: gTTS and local FFmpeg used.
')
            
    with zipfile.ZipFile('slice_package.zip', 'w') as zf:
        zf.write('capabilities.md')
        zf.write('slice.mp4')
    
    print('PROGRESS: yes - Generated new fast-paced slice.mp4 and updated slice_package.zip')

if __name__ == '__main__':
    make()
