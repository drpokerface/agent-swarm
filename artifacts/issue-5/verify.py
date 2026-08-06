# VALIDATED: True
import os
import sys
import random
import shutil
import zipfile
import subprocess
import re

def bootstrap():
    try:
        from google import genai
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai"])

bootstrap()
from google import genai

def evaluate_zip(zip_path, run_llm=True):
    c1 = os.path.exists(zip_path)
    if not c1:
        return False, False, False, False, 0.0
    
    c2 = True
    c3 = False
    c4 = True
    score = 0.0
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            bad_file = z.testzip()
            if bad_file is not None:
                c2 = False
                
            namelist = z.namelist()
            count = len(namelist)
            c3 = (count == 30)
            
            for name in namelist:
                info = z.getinfo(name)
                if info.file_size == 0 or not name.lower().endswith(('.mp3', '.wav', '.ogg')):
                    c4 = False
                    break
            
            if run_llm and count > 0:
                dialogue_files = [n for n in namelist if n.startswith('dialogue_')]
                if dialogue_files:
                    sampled = random.sample(dialogue_files, min(len(dialogue_files), 3))
                    scores = []
                    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
                    os.makedirs('scratch/temp_judge', exist_ok=True)
                    for f_name in sampled:
                        extracted_path = z.extract(f_name, 'scratch/temp_judge')
                        try:
                            handle = client.files.upload(file=extracted_path)
                            prompt = "Listen to this audio. Score it from 1 to 5 on audio clarity, voice appropriateness, and delivery quality. Respond with ONLY the integer score."
                            response = client.models.generate_content(
                                model="gemini-3.5-flash",
                                contents=[prompt, handle]
                            ).text
                            match = re.search(r'\d+', response)
                            s = int(match.group()) if match else 1
                            scores.append(s)
                        except Exception:
                            scores.append(1)
                    if scores:
                        scores.sort()
                        score = scores[len(scores)//2]
    except Exception:
        c2 = False
        c3 = False
        c4 = False
        
    return c1, c2, c3, c4, score

def run_checks():
    c1, c2, c3, c4, score = evaluate_zip('audio.zip', run_llm=True)
    
    print(f"C1 (exists): {c1}")
    print(f"C2 (valid zip): {c2}")
    print(f"C3 (exactly 30 files): {c3}")
    print(f"C4 (non-zero sizes & valid extensions): {c4}")
    print(f"C5 (median quality >= 4): {score}")
    
    if not all([c1, c2, c3, c4, score >= 4.0]):
        sys.exit(1)
        
    os.makedirs('scratch', exist_ok=True)
    fault_path = 'scratch/fault_audio.zip'
    shutil.copy('audio.zip', fault_path)
    
    with open(fault_path, 'r+b') as f:
        f.seek(0)
        f.write(b'GARBAGE')
        
    fc1, fc2, fc3, fc4, fscore = evaluate_zip(fault_path, run_llm=False)
    if fc2 is False:
        print(f"FAULT-PROOF: caught corrupted zip file. C2 returned {fc2}")
    else:
        sys.exit(1)
        
    print("VERDICT: PASS")
    sys.exit(0)

if __name__ == "__main__":
    run_checks()
