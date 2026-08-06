import os
import sys
import subprocess
import json
import random
import shutil

def run_ffprobe(filepath):
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration:stream=codec_type,width,height', '-of', 'json', filepath]
    try:
        result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if result.returncode != 0: return None
        return json.loads(result.stdout)
    except Exception:
        return None

def verify(filepath, silent=False):
    if not os.path.exists(filepath):
        if not silent: print(f"C1: final.mp4 exists - FAILED (not found)")
        return False
    if not silent: print(f"C1: final.mp4 exists - PASS")

    probe = run_ffprobe(filepath)
    if not probe or 'streams' not in probe:
        if not silent: print("C2: ffprobe failed - FAILED")
        return False

    video_streams = [s for s in probe['streams'] if s.get('codec_type') == 'video']
    audio_streams = [s for s in probe['streams'] if s.get('codec_type') == 'audio']

    if not video_streams:
        if not silent: print("C2: video stream - FAILED (no video stream)")
        return False
    
    v_stream = video_streams[0]
    w, h = v_stream.get('width'), v_stream.get('height')
    if w != 1280 or h != 720:
        if not silent: print(f"C2: resolution 1280x720 - FAILED (got {w}x{h})")
        return False
    if not silent: print("C2: resolution 1280x720 - PASS")

    if not audio_streams:
        if not silent: print("C3: audio stream - FAILED (no audio)")
        return False
    if not silent: print("C3: audio stream - PASS")

    fmt = probe.get('format', {})
    duration_str = fmt.get('duration')
    if not duration_str:
        if not silent: print("C4: duration 110-130s - FAILED (no duration)")
        return False
    
    duration = float(duration_str)
    if not (110 <= duration <= 130):
        if not silent: print(f"C4: duration 110-130s - FAILED (got {duration:.2f}s)")
        return False
    if not silent: print(f"C4: duration 110-130s - PASS ({duration:.2f}s)")
    
    return True

def main():
    print("FAULT-PROOF: starting")
    os.makedirs("scratch", exist_ok=True)
    fault_file = f"scratch/fault_{random.randint(1000, 9999)}.mp4"
    with open(fault_file, "wb") as f:
        f.write(b"not a video")
    
    if verify(fault_file, silent=True) is False:
        print(f"FAULT-PROOF: correctly caught induced fault in corrupted file {fault_file}")
    else:
        print("FAULT-PROOF: failed to catch fault!")
        sys.exit(1)
        
    print("\nReal artifact check:")
    if verify("final.mp4"):
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)

if __name__ == '__main__':
    main()
