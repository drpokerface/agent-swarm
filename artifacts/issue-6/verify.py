# verify.py
import os
import subprocess
import sys
import shutil
import random

def run_cmd(cmd):
    res = subprocess.run(cmd, capture_output=True, text=True)
    return res.stdout.strip(), res.stderr.strip(), res.returncode

def check_c1_c2():
    if not os.path.exists('final.mp4'): return False
    cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=p=0', 'final.mp4']
    out, err, code = run_cmd(cmd)
    if code != 0 or out != '1280,720': return False
    cmd_a = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_type', '-of', 'csv=p=0', 'final.mp4']
    out, err, code = run_cmd(cmd_a)
    if code != 0 or 'audio' not in out: return False
    cmd_d = ['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', 'final.mp4']
    out, err, code = run_cmd(cmd_d)
    if code != 0: return False
    try:
        duration = float(out)
        if not (115 <= duration <= 125): return False
    except: return False
    return True

def check_c3():
    if not os.path.exists('final.mp4'): return False
    cmd = ['ffmpeg', '-i', 'final.mp4', '-af', 'silencedetect=noise=-40dB:d=1.5', '-f', 'null', '-']
    out, err, code = run_cmd(cmd)
    if 'silence_start' in err: return False
    return True

def check_all(target='final.mp4'):
    # replace final.mp4 with target in commands if needed, but keeping it simple for now
    return False # RED state

if __name__ == '__main__':
    print("VERDICT: FAIL - Not implemented")
    sys.exit(1)
