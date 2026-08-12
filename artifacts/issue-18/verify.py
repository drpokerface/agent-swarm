import os
import subprocess
import json

def get_info(path):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'stream=width,height,duration,codec_type', '-of', 'json', path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if not res.stdout.strip(): return None
    return json.loads(res.stdout)

def check(path='final.mp4'):
    if not os.path.exists(path): return False
    info = get_info(path)
    if not info or 'streams' not in info: return False
    has_video = False
    has_audio = False
    for s in info['streams']:
        if s.get('codec_type') == 'video':
            if s.get('width') != 1280 or s.get('height') != 720: return False
            dur = float(s.get('duration', 0))
            if dur < 60: return False
            has_video = True
        if s.get('codec_type') == 'audio':
            has_audio = True
    return has_video and has_audio

if __name__ == '__main__':
    os.makedirs('scratch', exist_ok=True)
    fault_path = 'scratch/fault_test.mp4'
    os.system(f"ffmpeg -y -f lavfi -i color=c=black:s=640x360:d=1 -c:v libx264 {fault_path} >/dev/null 2>&1")
    if not check(fault_path):
        print("FAULT-PROOF: Caught incorrect resolution video")
    else:
        print("FAULT-PROOF: Failed to catch fault")
        exit(1)
        
    if check('final.mp4'):
        print("C1: final.mp4 exists")
        print("C2: 1280x720")
        print("C3: duration >=60s")
        print("C4: has audio")
        print("VERDICT: PASS")
    else:
        print("VERDICT: FAIL")
        exit(1)
