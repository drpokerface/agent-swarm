import os
import json
import subprocess
import shutil

script_file = "artifacts/issue-21/script.json"
assets_dir = "scratch/assets"

with open(script_file) as f:
    script_data = json.load(f)

scene_videos = []

for i, scene in enumerate(script_data, 1):
    image_file = f"{assets_dir}/scene_{i}.jpg"
    
    line_idx = 1
    audio_files = []
    while True:
        audio_file = f"{assets_dir}/scene_{i}_line_{line_idx}.wav"
        if os.path.exists(audio_file):
            audio_files.append(audio_file)
            line_idx += 1
        else:
            break
            
    scene_audio = f"scratch/scene_{i}_audio.wav"
    if len(audio_files) > 1:
        concat_file = f"scratch/scene_{i}_audio_concat.txt"
        with open(concat_file, "w") as f:
            for af in audio_files:
                p = os.path.abspath(af).replace('\\', '/')
                f.write(f"file '{p}'\n")
        subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file, "-c", "copy", scene_audio], check=True, capture_output=True)
    elif len(audio_files) == 1:
        shutil.copy(audio_files[0], scene_audio)
    else:
        subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=22050:cl=mono", "-t", "5", scene_audio], check=True)
    
    dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", scene_audio]
    dur_res = subprocess.run(dur_cmd, capture_output=True, text=True)
    duration = float(dur_res.stdout.strip())
    
    scene_video = f"scratch/scene_{i}.mp4"
    subprocess.run([
        "ffmpeg", "-y",
        "-loop", "1", "-framerate", "24", "-i", image_file,
        "-i", scene_audio,
        "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "192k",
        "-pix_fmt", "yuv420p",
        "-vf", "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2",
        "-t", str(duration),
        scene_video
    ], check=True, capture_output=True)
    
    scene_videos.append(scene_video)

final_concat_file = "scratch/final_concat.txt"
with open(final_concat_file, "w") as f:
    for sv in scene_videos:
        p = os.path.abspath(sv).replace('\\', '/')
        f.write(f"file '{p}'\n")

subprocess.run(["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", final_concat_file, "-c", "copy", "final.mp4"], check=True, capture_output=True)
print("Rough cut assembled to final.mp4")

dur_cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", "final.mp4"]
dur_res = subprocess.run(dur_cmd, capture_output=True, text=True)
print(f"final.mp4 actual duration: {dur_res.stdout.strip()}s")
