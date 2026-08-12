# verify.py - validates the visual assets package
import os
import sys
import zipfile
import json
import random
import shutil

try:
    from PIL import Image
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "google-genai"])
    from PIL import Image

def get_characters():
    with open('artifacts/issue-15/script.json') as f:
        script = json.load(f)
    chars = set()
    for item in script:
        cs = item.get('character_state', '')
        if ':' in cs:
            chars.add(cs.split(':')[0].strip())
    return chars

def verify_zip(zip_path):
    if not os.path.exists(zip_path):
        return False, f"{zip_path} not found"
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            bad = z.testzip()
            if bad is not None:
                return False, f"Corrupted file in zip: {bad}"
    except Exception as e:
        return False, f"Invalid zip: {e}"
    return True, "Valid zip"

def verify_backgrounds(zip_path, expected_count=38):
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            names = z.namelist()
            for i in range(1, expected_count + 1):
                bg_name = f"backgrounds/bg_{i:02d}.png"
                if bg_name not in names:
                    return False, f"Missing {bg_name}"
                with z.open(bg_name) as f:
                    img = Image.open(f)
                    if img.size != (1280, 720):
                        return False, f"{bg_name} is {img.size}, expected (1280, 720)"
    except Exception as e:
        return False, f"Background verification failed: {e}"
    return True, "Backgrounds valid"

def verify_characters(zip_path, chars):
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            names = z.namelist()
            for char in chars:
                for state in ['talking', 'silent']:
                    char_name = f"characters/{char}_{state}.png"
                    if char_name not in names:
                        return False, f"Missing {char_name}"
                    with z.open(char_name) as f:
                        img = Image.open(f)
                        if img.mode not in ('RGBA', 'LA', 'PA') and 'transparency' not in img.info:
                            if img.mode != 'RGBA':
                                return False, f"{char_name} is not RGBA (is {img.mode})"
                        
                        if img.mode == 'RGBA':
                            extrema = img.getextrema()
                            if extrema[3][0] == 255: 
                                return False, f"{char_name} has no transparent pixels"
    except Exception as e:
        return False, f"Character verification failed: {e}"
    return True, "Characters valid"

def verify_style(zip_path):
    from google import genai
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    
    with zipfile.ZipFile(zip_path, 'r') as z:
        bgs = [n for n in z.namelist() if n.startswith('backgrounds/') and n.endswith('.png')]
        chars = [n for n in z.namelist() if n.startswith('characters/') and n.endswith('.png')]
        
        if not bgs or not chars:
            return False, "Not enough images to judge"
            
        sample_bgs = random.sample(bgs, min(3, len(bgs)))
        sample_chars = random.sample(chars, min(3, len(chars)))
        
        os.makedirs('scratch/judge', exist_ok=True)
        files_to_upload = []
        for n in sample_bgs + sample_chars:
            p = z.extract(n, 'scratch/judge')
            files_to_upload.append(p)
            
        uploaded = []
        for p in files_to_upload:
            uploaded.append(client.files.upload(file=p))
            
        rubric = '''Score the style of these animation assets (backgrounds and characters) from 1 to 10.
Criteria:
- Must look like a 2D adult animated comedy (e.g. South Park, Family Guy).
- Must have a consistent irreverent style.
- Characters must be cutout-style or flat vector style.
- Backgrounds must match the character style (not hyper-realistic, not 3D).
Respond with a JSON object: {"score": <int>, "reasoning": "<string>"}
'''
        scores = []
        for _ in range(3):
            try:
                resp = client.models.generate_content(
                    model="gemini-3.5-pro",
                    contents=[rubric] + uploaded,
                    config={"response_mime_type": "application/json"}
                )
                data = json.loads(resp.text)
                scores.append(data.get("score", 0))
            except Exception as e:
                return False, f"Judge error: {e}"
                
        if len(scores) == 3:
            scores.sort()
            median = scores[1]
            if median >= 7:
                return True, f"Style median score {median}/10"
            else:
                return False, f"Style median score {median}/10 is below 7"
        return False, "Could not get 3 scores"

def fault_proof():
    os.makedirs('scratch/fp', exist_ok=True)
    bad_zip = 'scratch/bad_visuals.zip'
    
    img = Image.new('RGB', (800, 600), color='red')
    img.save('scratch/fp/bg_01.png')
    
    with zipfile.ZipFile(bad_zip, 'w') as z:
        z.write('scratch/fp/bg_01.png', 'backgrounds/bg_01.png')
        
    ok, msg = verify_backgrounds(bad_zip, 38)
    if ok:
        print("FAULT-PROOF FAILED: Did not catch bad background size or missing files")
        return False
    print(f"FAULT-PROOF: Caught bad zip: {msg}")
    return True

def main():
    print("EXPECT: Verification of visuals.zip")
    if not fault_proof():
        sys.exit(1)
        
    chars = get_characters()
    zip_path = 'visuals.zip'
    
    c1, msg1 = verify_zip(zip_path)
    print(f"C1 (Valid Zip): {msg1}")
    if not c1: sys.exit(1)
    
    c2, msg2 = verify_backgrounds(zip_path, 38)
    print(f"C2 (Backgrounds): {msg2}")
    if not c2: sys.exit(1)
    
    c3, msg3 = verify_characters(zip_path, chars)
    print(f"C3 (Characters): {msg3}")
    if not c3: sys.exit(1)
    
    c4, msg4 = verify_style(zip_path)
    print(f"C4 (Style): {msg4}")
    if not c4: sys.exit(1)
    
    print("VERDICT: PASS")

if __name__ == '__main__':
    main()
