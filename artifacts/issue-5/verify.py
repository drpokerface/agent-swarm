import os
import sys
import json
import zipfile
import random
import shutil
import subprocess

try:
    import mutagen
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "mutagen", "--quiet"])
    import mutagen

def verify_artifact(zip_path, extract_dir):
    if not os.path.exists(zip_path):
        print(f"Claim C1 failed: {zip_path} does not exist.")
        return False
    if not zipfile.is_zipfile(zip_path):
        print(f"Claim C2 failed: {zip_path} is not a valid zip file.")
        return False

    os.makedirs(extract_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)
    except Exception as e:
        print(f"Claim C2 failed: could not extract {zip_path}: {e}")
        return False

    with open("artifacts/issue-3/script.json", "r", encoding="utf-8") as f:
        script = json.load(f)

    # Check C3, C4, C6
    for s_idx, scene in enumerate(script.get('scenes', [])):
        s_id = scene.get('id', s_idx + 1)
        
        for d_idx, d in enumerate(scene.get('dialogue', [])):
            speaker = d["speaker"]
            f_mp3 = os.path.join(extract_dir, f"scene_{s_id}_dialogue_{d_idx}_{speaker}.mp3")
            f_wav = os.path.join(extract_dir, f"scene_{s_id}_dialogue_{d_idx}_{speaker}.wav")
            f_path = f_mp3 if os.path.exists(f_mp3) else (f_wav if os.path.exists(f_wav) else None)
            
            if not f_path:
                print(f"Claim C3 failed: Missing audio for Scene {s_id}, dialogue {d_idx} ({speaker})")
                return False
                
            try:
                m = mutagen.File(f_path)
                if m is None or m.info.length <= 0:
                    print(f"Claim C6 failed: {f_path} is not a valid playable audio file or has 0 duration.")
                    return False
            except Exception as e:
                print(f"Claim C6 failed: {f_path} could not be parsed as audio by mutagen: {e}")
                return False

        for c_idx, c in enumerate(scene.get('audio_cues', [])):
            f_mp3 = os.path.join(extract_dir, f"scene_{s_id}_cue_{c_idx}.mp3")
            f_wav = os.path.join(extract_dir, f"scene_{s_id}_cue_{c_idx}.wav")
            f_path = f_mp3 if os.path.exists(f_mp3) else (f_wav if os.path.exists(f_wav) else None)
            
            if not f_path:
                print(f"Claim C4 failed: Missing audio for Scene {s_id}, cue {c_idx}")
                return False
                
            try:
                m = mutagen.File(f_path)
                if m is None or m.info.length <= 0:
                    print(f"Claim C6 failed: {f_path} is not a valid playable audio file or has 0 duration.")
                    return False
            except Exception as e:
                print(f"Claim C6 failed: {f_path} could not be parsed as audio by mutagen: {e}")
                return False
                
    return True

def create_corrupted_zip(original_zip, corrupted_zip):
    temp_dir = f"scratch/temp_corrupt_{random.randint(1000,9999)}"
    os.makedirs(temp_dir, exist_ok=True)
    with zipfile.ZipFile(original_zip, 'r') as zip_ref:
        zip_ref.extractall(temp_dir)
    
    files = []
    for root, _, fnames in os.walk(temp_dir):
        for fname in fnames:
            files.append(os.path.join(root, fname))
            
    if not files:
        return False
        
    file_to_remove = random.choice(files)
    os.remove(file_to_remove)
    
    with zipfile.ZipFile(corrupted_zip, 'w') as zip_ref:
        for root, _, fnames in os.walk(temp_dir):
            for fname in fnames:
                file_path = os.path.join(root, fname)
                arcname = os.path.relpath(file_path, temp_dir)
                zip_ref.write(file_path, arcname)
                
    shutil.rmtree(temp_dir)
    return True

def main():
    print("Checking real artifact...")
    real_zip = "audio.zip"
    real_extract = "scratch/unzip_real"
    if not verify_artifact(real_zip, real_extract):
        print("Real artifact verification failed.")
        sys.exit(1)
        
    print("Real artifact passed. Running fault-proof...")
    corrupted_zip = f"scratch/audio_corrupted_{random.randint(1000,9999)}.zip"
    corrupt_extract = f"scratch/unzip_corrupted_{random.randint(1000,9999)}"
    
    if not create_corrupted_zip(real_zip, corrupted_zip):
        print("Failed to create corrupted zip.")
        sys.exit(1)
        
    if verify_artifact(corrupted_zip, corrupt_extract):
        print("Fault-proof failed: verify_artifact returned True for a corrupted zip.")
        sys.exit(1)
        
    print("FAULT-PROOF: Successfully detected missing file in corrupted zip.")
    print("VERDICT: PASS")
    sys.exit(0)

if __name__ == "__main__":
    main()
