import sys
import os
import json
import zipfile
import subprocess
import random
import string

def check_criteria(zip_path="audio.zip", script_path="artifacts/issue-9/script.json"):
    if not os.path.exists(zip_path):
        return False, "C1 FAILED: audio.zip does not exist"
    if not zipfile.is_zipfile(zip_path):
        return False, "C1 FAILED: audio.zip is not a valid zip file"
    print("C1 PASS: audio.zip exists and is valid")
        
    extract_dir = "scratch/verify_extract_" + ''.join(random.choices(string.ascii_lowercase, k=6))
    os.makedirs(extract_dir, exist_ok=True)
    with zipfile.ZipFile(zip_path, 'r') as zf:
        zf.extractall(extract_dir)
        
    manifest_path = os.path.join(extract_dir, "manifest.json")
    if not os.path.exists(manifest_path):
        return False, "C2 FAILED: manifest.json not found in audio.zip"
    print("C2 PASS: manifest.json found")
        
    try:
        with open(manifest_path, "r") as f:
            manifest = json.load(f)
    except Exception as e:
        return False, f"C3 FAILED: manifest.json is not valid JSON: {e}"
        
    if "dialogue" not in manifest or "bgm" not in manifest or "sfx" not in manifest:
        return False, "C3 FAILED: manifest.json missing required keys (dialogue, bgm, sfx)"
        
    with open(script_path, "r") as f:
        script = json.load(f)
        
    total_lines = sum(len(scene.get("dialogue", [])) for scene in script.get("scenes", []))
    if len(manifest["dialogue"]) != total_lines:
        return False, f"C3 FAILED: manifest dialogue count ({len(manifest['dialogue'])}) != script dialogue count ({total_lines})"
    print(f"C3 PASS: manifest matches script lines ({total_lines})")
        
    referenced_files = []
    for d in manifest["dialogue"]:
        if "file" not in d:
            return False, "C4 FAILED: Dialogue entry missing 'file' key"
        referenced_files.append(d["file"])
        
    if isinstance(manifest["bgm"], str) and manifest["bgm"]:
        referenced_files.append(manifest["bgm"])
    elif isinstance(manifest["bgm"], list):
        referenced_files.extend(manifest["bgm"])
        
    if isinstance(manifest["sfx"], list):
        referenced_files.extend(manifest["sfx"])
        
    if not referenced_files:
        return False, "C4 FAILED: No audio files referenced in manifest"
        
    for f_name in referenced_files:
        f_path = os.path.join(extract_dir, f_name)
        if not os.path.exists(f_path):
            return False, f"C4 FAILED: Referenced file {f_name} not found in zip"
            
        try:
            cmd = ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", f_path]
            res = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if res.returncode != 0:
                return False, f"C4 FAILED: ffprobe failed for {f_name}: {res.stderr}"
            duration = float(res.stdout.strip())
            if duration <= 0:
                return False, f"C4 FAILED: File {f_name} has invalid duration {duration}"
        except Exception as e:
            return False, f"C4 FAILED: Failed to probe {f_name}: {e}"
    print("C4 PASS: all referenced files are valid audio")
    
    return True, "All technical criteria passed"

def run_fault_proof():
    print("\nRunning FAULT-PROOF:")
    os.makedirs("scratch/fault_proof", exist_ok=True)
    script = {"scenes": [{"dialogue": [{"line": "test"}]}]}
    with open("scratch/fault_proof/fake_script.json", "w") as f:
        json.dump(script, f)
        
    manifest = {"dialogue": [{"file": "missing.wav"}], "bgm": [], "sfx": []}
    with open("scratch/fault_proof/manifest.json", "w") as f:
        json.dump(manifest, f)
    
    fault_zip = "scratch/fault_proof/fault.zip"
    with zipfile.ZipFile(fault_zip, 'w') as zf:
        zf.write("scratch/fault_proof/manifest.json", "manifest.json")
        
    ok, msg = check_criteria(fault_zip, "scratch/fault_proof/fake_script.json")
    if ok:
        print("FAULT-PROOF FAILED: Did not catch missing audio file.")
        return False
    else:
        print(f"FAULT-PROOF: Caught induced fault -> {msg}")
        return True

if __name__ == '__main__':
    if not run_fault_proof():
        sys.exit(1)
        
    print("\nRunning Verification on Real Artifacts:")
    ok, msg = check_criteria("audio.zip", "artifacts/issue-9/script.json")
    if ok:
        print("VERDICT: PASS")
    else:
        print(f"VERDICT: FAILED - {msg}")
        sys.exit(1)
