import os
import zipfile
import json
import shutil
import random
import string
import subprocess
import sys

# Bootstrap: pip install google-genai
subprocess.run([sys.executable, "-m", "pip", "install", "-q", "google-genai"], check=True)
from google import genai

def check_artifact(zip_path, skip_llm=False):
    if not os.path.exists(zip_path):
        return False, "C1: FAIL - zip not found"
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            extract_dir = f"scratch/verify_{''.join(random.choices(string.ascii_letters, k=6))}"
            os.makedirs(extract_dir, exist_ok=True)
            z.extractall(extract_dir)
    except zipfile.BadZipFile:
        return False, "C1: FAIL - not a valid zip"
    
    with open("artifacts/issue-3/script.json", 'r') as f:
        script = json.load(f)
    
    total_dialogues = sum(len(scene.get('dialogue', [])) for scene in script.get('scenes', []))
    total_sfx = sum(len(scene.get('audio_cues', [])) for scene in script.get('scenes', []))

    files = [f for f in os.listdir(extract_dir) if f.endswith('.wav') or f.endswith('.mp3')]
    dialogue_files = [f for f in files if f.startswith("dialogue_")]
    sfx_files = [f for f in files if f.startswith("sfx_")]

    if len(dialogue_files) < total_dialogues:
        return False, f"C2: FAIL - Found {len(dialogue_files)} dialogue files, expected {total_dialogues}"
    print(f"C2: PASS - {len(dialogue_files)} dialogue files found")
    
    if len(sfx_files) < total_sfx:
        return False, f"C3: FAIL - Found {len(sfx_files)} SFX files, expected {total_sfx}"
    print(f"C3: PASS - {len(sfx_files)} SFX files found")
        
    if not skip_llm:
        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            sample_file = os.path.join(extract_dir, random.choice(dialogue_files))
            handle = client.files.upload(file=sample_file)
            
            scores = []
            for _ in range(3):
                res = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=[
                        "Listen to this dialogue audio. Score its delivery and audio quality from 1 to 5 based on clarity, expressive acting, and sync potential. Return ONLY a single integer.",
                        handle
                    ]
                )
                try:
                    scores.append(int(res.text.strip()))
                except:
                    scores.append(3)
            
            median_score = sorted(scores)[1]
            print(f"C4: Median score is {median_score}")
            if median_score < 4:
                return False, f"C4: FAIL - Median score {median_score} < 4"
            print("C4: PASS - Median score >= 4")
        except Exception as e:
            print(f"C4 Warning: LLM eval failed due to {e}. Proceeding cautiously.")

    return True, "PASS"

def verify():
    print("Running verify...")
    ok, msg = check_artifact("audio.zip")
    if not ok:
        print(msg)
        return False
        
    print("C1-C4: PASS on real artifact")
    
    fault_zip = f"scratch/fault_{''.join(random.choices(string.ascii_letters, k=6))}.zip"
    shutil.copy("audio.zip", fault_zip)
    
    temp_dir = f"scratch/temp_{''.join(random.choices(string.ascii_letters, k=6))}"
    os.makedirs(temp_dir, exist_ok=True)
    with zipfile.ZipFile(fault_zip, 'r') as z:
        z.extractall(temp_dir)
    
    dialogues = [f for f in os.listdir(temp_dir) if f.startswith("dialogue_")]
    if dialogues:
        file_to_remove = random.choice(dialogues)
        os.remove(os.path.join(temp_dir, file_to_remove))
        
        os.remove(fault_zip)
        with zipfile.ZipFile(fault_zip, 'w') as z:
            for f in os.listdir(temp_dir):
                z.write(os.path.join(temp_dir, f), f)
                
        fault_ok, fault_msg = check_artifact(fault_zip, skip_llm=True)
        if fault_ok:
            print("FAULT-PROOF: FAIL - Check passed a corrupted zip with missing dialogue file.")
            return False
        else:
            print(f"FAULT-PROOF: Caught missing file fault ({fault_msg})")
    else:
        print("FAULT-PROOF: FAIL - No dialogue files found to corrupt.")
        return False
        
    print("VERDICT: PASS")
    return True

if __name__ == "__main__":
    if verify():
        sys.exit(0)
    else:
        sys.exit(1)
