#!/usr/bin/env python3
import os
import sys
import subprocess
import random
import shutil

def run_cmd(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        out, err = p.communicate()
        return p.returncode, out.strip(), err.strip()
    except FileNotFoundError:
        return -1, "", "Binary not found"

def check_c1():
    if not os.path.exists("capabilities.md"): return False, "capabilities.md missing"
    content = open("capabilities.md", "r", encoding="utf-8").read().lower()
    if "ffmpeg" not in content: return False, "missing ffmpeg mention"
    if "api_key" not in content and "api key" not in content and "gemini" not in content: return False, "missing API checks"
    return True, "capabilities.md exists and contains audits"

def check_c2(filepath):
    if not os.path.exists(filepath): return False, f"{filepath} missing"
    return True, f"{filepath} exists"

def check_c3(filepath):
    rc, out, err = run_cmd(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height", "-of", "csv=s=x:p=0", filepath])
    if rc != 0: return False, f"ffprobe failed: {err}"
    parts = out.split('x')
    if len(parts) != 2: return False, "unparseable resolution"
    try:
        if int(parts[0]) == 1280 and int(parts[1]) == 720:
            return True, "Resolution is 1280x720"
        return False, f"Resolution is {out}"
    except:
        return False, "Resolution parse failed"

def check_c4(filepath):
    rc_v, out_v, _ = run_cmd(["ffprobe", "-v", "error", "-select_streams", "v", "-show_entries", "stream=codec_type", "-of", "csv=p=0", filepath])
    if "video" not in out_v: return False, "No video stream"
    rc_a, out_a, _ = run_cmd(["ffprobe", "-v", "error", "-select_streams", "a", "-show_entries", "stream=codec_type", "-of", "csv=p=0", filepath])
    if "audio" not in out_a: return False, "No audio stream"
    return True, "Contains active video and audio streams"

def check_c5(filepath):
    rc, out, err = run_cmd(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", filepath])
    if rc != 0: return False, f"ffprobe format=duration failed: {err}"
    try:
        dur = float(out)
        if 8.0 <= dur <= 15.0:
            return True, f"Duration is {dur} seconds"
        return False, f"Duration {dur} not between 8.0 and 15.0"
    except:
        return False, "Duration parse failed"

def check_c6(filepath):
    os.makedirs("scratch", exist_ok=True)
    f1 = "scratch/c6_f1.jpg"
    f2 = "scratch/c6_f2.jpg"
    if os.path.exists(f1): os.remove(f1)
    if os.path.exists(f2): os.remove(f2)
    run_cmd(["ffmpeg", "-y", "-i", filepath, "-ss", "00:00:02", "-vframes", "1", f1])
    run_cmd(["ffmpeg", "-y", "-i", filepath, "-ss", "00:00:08", "-vframes", "1", f2])
    if not os.path.exists(f1) or not os.path.exists(f2):
        return False, "Could not extract frames for cut detection"
    s1 = os.path.getsize(f1)
    s2 = os.path.getsize(f2)
    if s1 == 0 or s2 == 0: return False, "Extracted frames are empty"
    diff = abs(s1 - s2) / max(s1, s2)
    if diff > 0.05:
        return True, "Visual cut detected (frame sizes differ)"
    return False, f"No visual cut detected (diff {diff:.3f} <= 0.05)"

def check_all(filepath):
    results = {}
    r1, m1 = check_c1()
    results['C1'] = (r1, m1)
    r2, m2 = check_c2(filepath)
    results['C2'] = (r2, m2)
    if r2:
        results['C3'] = check_c3(filepath)
        results['C4'] = check_c4(filepath)
        results['C5'] = check_c5(filepath)
        results['C6'] = check_c6(filepath)
    else:
        for k in ['C3', 'C4', 'C5', 'C6']: results[k] = (False, "Skipped (C2 failed)")
    return results

if __name__ == "__main__":
    os.makedirs("scratch", exist_ok=True)
    print("=== FAULT-PROOF ===")
    if os.path.exists("slice.mp4"):
        rand_id = random.randint(1000, 9999)
        corrupted = f"scratch/faulty_{rand_id}.mp4"
        shutil.copy("slice.mp4", corrupted)
        with open(corrupted, "r+b") as f:
            f.seek(max(0, os.path.getsize(corrupted) // 2))
            f.write(b"GARBAGE" * 1024)
        results_faulty = check_all(corrupted)
        caught = False
        for k, (passed, msg) in results_faulty.items():
            if k in ['C3', 'C4', 'C5', 'C6'] and passed == False:
                caught = True
                print(f"FAULT-PROOF: {k} check successfully caught corruption ({msg})")
                break
        if not caught:
            print("FAULT-PROOF: FAILED to catch corruption. All checks passed on corrupted file.")
            sys.exit(1)
    else:
        print("C2: slice.mp4 does not exist. Fault proof skipped.")
    
    print("\n=== ARTIFACT VERIFICATION ===")
    results_real = check_all("slice.mp4")
    all_passed = True
    for k, (passed, msg) in results_real.items():
        print(f"{k}: {passed} - {msg}")
        if not passed: all_passed = False
        
    if all_passed:
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)
