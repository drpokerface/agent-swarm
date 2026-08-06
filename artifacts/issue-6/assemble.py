
import os, glob, json
import numpy as np
from PIL import Image
from moviepy.editor import AudioFileClip, CompositeAudioClip, VideoClip

print("Loading audio clips...")
audio_clips = []

dialogue_files = glob.glob('assets/audio/dialogue_*.mp3')
for df in dialogue_files:
    basename = os.path.basename(df)
    parts = basename.replace('.mp3', '').split('_')
    t = float(parts[1])
    speaker = parts[2]
    clip = AudioFileClip(df).set_start(t)
    audio_clips.append({'clip': clip, 'speaker': speaker, 'start': t, 'end': t + clip.duration})

cues = {
    'cue_scene0_0.wav': 0.0,
    'cue_scene0_1.wav': 3.0,
    'cue_scene0_2.wav': 21.0,
    'cue_scene1_0.wav': 25.0,
    'cue_scene1_1.wav': 68.0,
    'cue_scene2_0.wav': 82.0,
    'cue_scene2_1.wav': 118.0,
}

for cue_name, t in cues.items():
    path = os.path.join('assets/audio', cue_name)
    if os.path.exists(path):
        clip = AudioFileClip(path).set_start(t)
        audio_clips.append({'clip': clip, 'speaker': 'SFX', 'start': t, 'end': t + clip.duration})

final_audio = CompositeAudioClip([a['clip'] for a in audio_clips])

print("Loading visual assets...")
images = {}
for path in glob.glob('assets/visuals/*.png'):
    img = Image.open(path).convert("RGBA")
    name = os.path.basename(path)
    if name.startswith('bg_'):
        img = img.resize((1280, 720))
    images[name] = img
    
def paste_img(bg, fg, pos):
    bg.paste(fg, pos, fg)
    
def make_frame(t):
    if 21.0 <= t < 24.0:
        bg = images['bg_barista_cutaway.png'].copy()
        barista = images['barista_screaming.png']
        paste_img(bg, barista, (400, 100))
        return np.array(bg.convert("RGB"))
        
    if 68.0 <= t < 72.0:
        bg = images['bg_bear_cutaway.png'].copy()
        bear = images['bear_badge.png']
        camper = images['camper_scared.png']
        paste_img(bg, bear, (300, 150))
        paste_img(bg, camper, (800, 250))
        return np.array(bg.convert("RGB"))
        
    if 74.0 <= t < 80.0:
        bg = images['bg_split_screen_router_fire.png'].copy()
    else:
        bg = images['bg_split_screen.png'].copy()
        
    dave_speaking = False
    zalgor_speaking = False
    for a in audio_clips:
        if a['speaker'] == 'DAVE' and a['start'] <= t <= a['end']:
            dave_speaking = True
        if a['speaker'] == 'ZALGOR' and a['start'] <= t <= a['end']:
            zalgor_speaking = True
            
    if dave_speaking:
        dave_img = images['dave_open.png'] if int(t * 10) % 2 == 0 else images['dave_o.png']
    else:
        dave_img = images['dave_sweating.png'] if 80 <= t < 120 else images['dave_neutral.png']
        
    if zalgor_speaking:
        zalgor_img = images['zalgor_open.png'] if int(t * 10) % 2 == 0 else images['zalgor_o.png']
    else:
        zalgor_img = images['zalgor_pitchfork.png'] if 80 <= t < 120 else images['zalgor_neutral.png']
        
    paste_img(bg, dave_img, (100, 250))
    paste_img(bg, zalgor_img, (750, 250))
    
    return np.array(bg.convert("RGB"))
    
print("Generating video...")
video = VideoClip(make_frame, duration=120)
video = video.set_audio(final_audio)
video.write_videofile('final.mp4', fps=10, codec='libx264', audio_codec='aac', logger=None)
print("SUCCESS!")
