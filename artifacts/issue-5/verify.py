import os
import json
import zipfile
import random
import shutil
import sys

def check_artifact(zip_path):
    if not os.path.exists(zip_path):
        return False, "file not found"

    with open('artifacts/issue-3/script.json', 'r') as f:
        script_data = json.load(f)

    expected = []
    dialogue_idx = 0
    sfx_idx = 0
    for scene in script_data.get('scenes', []):
        for cue in scene.get('audio_cues', []):
            expected.append(f'sfx_{sfx_idx}.mp3')
            sfx_idx += 1
        for dlg in scene.get('dialogue', []):
            expected.append(f'dialogue_{dialogue_idx}.mp3')
            dialogue_idx += 1

    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            zip_files = set(z.namelist())
            
            missing = set(expected) - zip_files
            if missing:
                return False, f"missing files: {missing}"
            
            for fname in expected:
                info = z.getinfo(fname)
                if info.file_size < 100:
                    return False, f"{fname} is too small ({info.file_size} bytes)"
    except Exception as e:
        return False, f"corrupted zip: {e}"

    return True, "ok"

def run_fault_proof():
    os.makedirs('scratch', exist_ok=True)
    fault_zip = f'scratch/fault_{random.randint(1000, 9999)}.zip'
    if os.path.exists('audio.zip'):
        shutil.copy('audio.zip', fault_zip)
    else:
        return
        
    # Corrupt the copy
    with open(fault_zip, 'r+b') as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(random.randint(0, max(0, size - 100)))
        f.write(b'GARBAGE DATA' * 10)

    ok, msg = check_artifact(fault_zip)
    if not ok:
        print(f"FAULT-PROOF: Caught corrupted artifact: {msg}")
    else:
        print("FAULT-PROOF FAILED: Did not catch corrupted artifact")
        sys.exit(1)

def verify():
    # Check real artifact
    print("C1: ZIP Exists")
    if not os.path.exists('audio.zip'):
        print("FAIL: audio.zip missing")
        sys.exit(1)
        
    print("C2: Expected contents")
    ok, msg = check_artifact('audio.zip')
    if not ok:
        print(f"FAIL: {msg}")
        sys.exit(1)
        
    print("C3: Minimum quality proxy passed")
    
    run_fault_proof()
    print("VERDICT: PASS")

if __name__ == '__main__':
    verify()
