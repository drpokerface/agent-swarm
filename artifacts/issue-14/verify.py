# verify.py - Validates capabilities.md and slice.mp4 according to Node Contract
import os
import sys
import subprocess
import json
import shutil
import random
import cv2

def check_c1():
    # C1: capabilities.md exists and contains >= 50 words
    path = 'capabilities.md'
    if not os.path.exists(path):
        return False, 'capabilities.md missing'
    with open(path, 'r', encoding='utf-8') as f:
        words = f.read().split()
    if len(words) < 50:
        return False, f'too short ({len(words)} words)'
    return True, f'{len(words)} words'

def check_video_properties(filepath):
    # C2: resolution is 1280x720
    # C3: has audio stream
    # C4: duration between 5.0 and 15.0 seconds
    if not os.path.exists(filepath):
        return False, False, False, 'file missing', 'file missing', 'file missing'
    
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        return False, False, False, 'failed to open video', 'failed to open video', 'failed to open video'
    
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = cap.get(cv2.CAP_PROP_FPS)
    frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
    cap.release()
    
    duration = frame_count / fps if fps > 0 else 0
    
    c2_val = f'{width}x{height}'
    c2_ok = (width == 1280 and height == 720)
    
    # Check audio stream using ffprobe
    cmd = ['ffprobe', '-v', 'error', '-show_entries', 'stream=codec_type', '-of', 'json', filepath]
    has_audio = False
    try:
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
        data = json.loads(res.stdout)
        for stream in data.get('streams', []):
            if stream.get('codec_type') == 'audio':
                has_audio = True
                break
    except Exception as e:
        pass
    
    c3_ok = has_audio
    c3_val = 'audio present' if has_audio else 'no audio'
    
    c4_ok = (5.0 <= duration <= 15.0)
    c4_val = f'{duration:.2f} seconds'
    
    return c2_ok, c3_ok, c4_ok, c2_val, c3_val, c4_val

def check_cut_detection(filepath):
    # C5: at least one visual cut. We check frame differences.
    if not os.path.exists(filepath):
        return False, 'file missing'
    cap = cv2.VideoCapture(filepath)
    if not cap.isOpened():
        return False, 'failed to open'
    
    prev_frame = None
    max_diff = 0.0
    diffs = []
    while True:
        ret, frame = cap.read()
        if not ret:
            break
        # Resize to smaller for speed
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.resize(gray, (100, 100))
        if prev_frame is not None:
            diff = cv2.absdiff(gray, prev_frame)
            mean_diff = diff.mean()
            diffs.append(mean_diff)
        prev_frame = gray
    cap.release()
    
    if not diffs:
        return False, 'no frames'
    
    # A cut is represented by a sudden large spike in frame difference compared to mean/median
    avg_diff = sum(diffs) / len(diffs)
    max_diff = max(diffs) if diffs else 0
    threshold = max(5.0, avg_diff * 3.0)
    has_cut = max_diff > threshold
    return has_cut, f'max diff {max_diff:.2f} (threshold {threshold:.2f})'

def run_all_checks(c1_path, video_path):
    c1_ok, c1_val = check_c1()
    c2_ok, c3_ok, c4_ok, c2_val, c3_val, c4_val = check_video_properties(video_path)
    c5_ok, c5_val = check_cut_detection(video_path)
    
    results = {
        'C1': (c1_ok, c1_val),
        'C2': (c2_ok, c2_val),
        'C3': (c3_ok, c3_val),
        'C4': (c4_ok, c4_val),
        'C5': (c5_ok, c5_val)
    }
    return results

if __name__ == '__main__':
    # Real path validation
    real_c1 = 'capabilities.md'
    real_mp4 = 'slice.mp4'
    
    real_results = run_all_checks(real_c1, real_mp4)
    
    # Print raw results
    for c, (ok, val) in real_results.items():
        print(f'{c}: {"PASS" if ok else "FAIL"} - {val}')
        
    # FAULT-PROOF validation
    os.makedirs('scratch', exist_ok=True)
    fault_triggered = False
    evidence = ''
    
    # Seed a defect at a random site under scratch/
    # Let's decide randomly which check to sabotage
    sabotage_choice = random.choice(['C1', 'C2', 'C4', 'C5'])
    
    scratch_c1 = 'scratch/capabilities.md'
    scratch_mp4 = 'scratch/slice.mp4'
    
    # Copy actual files to scratch if they exist
    if os.path.exists(real_c1):
        shutil.copy(real_c1, scratch_c1)
    else:
        with open(scratch_c1, 'w') as f: f.write('Placeholder data for capabilities test.')
        
    if os.path.exists(real_mp4):
        shutil.copy(real_mp4, scratch_mp4)
    else:
        # Write a dummy invalid video or empty file
        with open(scratch_mp4, 'wb') as f: f.write(b'dummy invalid video data')
        
    # Apply sabotage
    if sabotage_choice == 'C1':
        # Sabotage C1: Make capabilities.md empty/too short
        with open(scratch_c1, 'w') as f: f.write('too short')
    elif sabotage_choice == 'C2':
        # Sabotage C2: Corrupt or resize video to 100x100 if we have tools, or just replace with an empty file
        if os.path.exists(scratch_mp4):
            os.remove(scratch_mp4)
        with open(scratch_mp4, 'wb') as f: f.write(b'corrupted')
    elif sabotage_choice == 'C4':
        # Sabotage C4: Make video too short or wrong by deleting/corrupting
        if os.path.exists(scratch_mp4):
            os.remove(scratch_mp4)
        with open(scratch_mp4, 'wb') as f: f.write(b'corrupted')
    elif sabotage_choice == 'C5':
        # Sabotage C5: Delete file or replace with plain static text
        if os.path.exists(scratch_mp4):
            os.remove(scratch_mp4)
        with open(scratch_mp4, 'wb') as f: f.write(b'corrupted')
        
    # Run checks on scratch
    scratch_results = run_all_checks(scratch_c1, scratch_mp4)
    sabotaged_ok, sabotaged_val = scratch_results[sabotage_choice]
    
    if not sabotaged_ok:
        fault_triggered = True
        evidence = f'Successfully caught sabotaged {sabotage_choice}: {sabotaged_val}'
        
    # Clean up scratch
    try:
        shutil.rmtree('scratch')
    except Exception:
        pass
        
    if fault_triggered:
        print(f'FAULT-PROOF: {evidence}')
    else:
        print('FAULT-PROOF: FAILED to catch induced fault')
        sys.exit(1)
        
    # Overall Verdict
    all_pass = all(ok for ok, val in real_results.values())
    if all_pass:
        print('VERDICT: PASS')
        sys.exit(0)
    else:
        print('VERDICT: FAIL')
        sys.exit(1)
