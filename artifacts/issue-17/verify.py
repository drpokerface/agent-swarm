import os
import sys
import subprocess
import shutil
import zipfile
import random
import json

try:
    from PIL import Image
    from google import genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow", "google-genai"])
    from PIL import Image
    from google import genai

def get_expected_counts():
    with open("artifacts/issue-15/script.json") as f:
        script = json.load(f)
    unique_bgs = set()
    chars = set()
    for item in script:
        if item.get('background'):
            unique_bgs.add(item['background'])
        state = item.get('character_state', '')
        if ':' in state:
            chars.add(state.split(':')[0].strip())
    return len(unique_bgs), list(chars)

def check_artifact(extract_dir):
    expected_bgs_count, expected_chars = get_expected_counts()
    
    # C2: backgrounds
    bg_dir = os.path.join(extract_dir, "backgrounds")
    if not os.path.isdir(bg_dir):
        return False, "No backgrounds directory"
    bgs = [f for f in os.listdir(bg_dir) if f.endswith('.png')]
    if len(bgs) != expected_bgs_count:
        return False, f"Expected {expected_bgs_count} backgrounds, got {len(bgs)}"
    for bg in bgs:
        with Image.open(os.path.join(bg_dir, bg)) as img:
            if img.size != (1280, 720):
                return False, f"Background {bg} has wrong size: {img.size}"

    # C3: characters
    char_dir = os.path.join(extract_dir, "characters")
    if not os.path.isdir(char_dir):
        return False, "No characters directory"
    for char in expected_chars:
        cdir = os.path.join(char_dir, char)
        if not os.path.isdir(cdir):
            return False, f"Missing character folder: {char}"
        for state in ["talking.png", "silent.png"]:
            p = os.path.join(cdir, state)
            if not os.path.isfile(p):
                return False, f"Missing {state} for {char}"
            with Image.open(p) as img:
                img = img.convert("RGBA")
                extrema = img.getextrema()
                if extrema[3][0] == 255:
                    return False, f"Character image {char}/{state} is not transparent"

    return True, "Check passed"

def check_style(extract_dir):
    bg_dir = os.path.join(extract_dir, "backgrounds")
    bgs = [f for f in os.listdir(bg_dir) if f.endswith('.png')]
    char_dir = os.path.join(extract_dir, "characters")
    
    if not bgs:
        return False, "No backgrounds to check style"
    bg_sample = os.path.join(bg_dir, random.choice(bgs))
    
    chars = os.listdir(char_dir)
    if not chars:
        return False, "No characters to check style"
    char_name = random.choice(chars)
    char_sample = os.path.join(char_dir, char_name, "silent.png")
    
    if not os.path.exists(char_sample):
        return False, "Missing character silent.png to check style"

    client = genai.Client()
    bg_file = client.files.upload(file=bg_sample)
    char_file = client.files.upload(file=char_sample)
    
    prompt = "Are these images highly consistent in style, and do they match an irreverent, satirical adult-animation cutout style (like Family Guy or South Park)? Answer YES or NO, followed by a brief reason."
    
    res = client.models.generate_content(
        model="gemini-3.5-flash",
        contents=[bg_file, char_file, prompt]
    )
    text = res.text.strip().upper()
    if text.startswith("YES"):
        return True, res.text
    else:
        return False, res.text

def run_fault_proof():
    print("Running FAULT PROOF...")
    os.makedirs("scratch/fault_proof/backgrounds", exist_ok=True)
    expected_bgs_count, expected_chars = get_expected_counts()
    
    for char in expected_chars:
        os.makedirs(f"scratch/fault_proof/characters/{char}", exist_ok=True)
    
    for i in range(expected_bgs_count):
        img = Image.new('RGB', (1280, 720), color = 'red')
        img.save(f"scratch/fault_proof/backgrounds/bg_{i}.png")
        
    for char in expected_chars:
        img = Image.new('RGBA', (100, 100), color = (255, 0, 0, 0))
        img.save(f"scratch/fault_proof/characters/{char}/talking.png")
        img.save(f"scratch/fault_proof/characters/{char}/silent.png")
        
    ok, msg = check_artifact("scratch/fault_proof")
    if not ok:
        print(f"Base fault proof setup failed: {msg}")
        return False
        
    fault_type = random.choice(['bg_size', 'char_opaque', 'missing_bg'])
    if fault_type == 'bg_size':
        img = Image.new('RGB', (800, 600), color = 'blue')
        img.save("scratch/fault_proof/backgrounds/bg_0.png")
    elif fault_type == 'char_opaque':
        char = expected_chars[0]
        img = Image.new('RGB', (100, 100), color = 'blue')
        img.save(f"scratch/fault_proof/characters/{char}/silent.png")
    elif fault_type == 'missing_bg':
        os.remove("scratch/fault_proof/backgrounds/bg_1.png")
        
    ok, msg = check_artifact("scratch/fault_proof")
    if ok:
        print("FAULT PROOF FAILED: Did not catch corruption!")
        return False
    else:
        print(f"FAULT-PROOF: Caught induced fault ({fault_type}): {msg}")
        return True

def verify_real():
    if not os.path.exists("visuals.zip"):
        print("C1: visuals.zip does not exist")
        return False
        
    print("C1: visuals.zip exists")
    
    extract_dir = "scratch/extracted_visuals"
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir)
    
    try:
        with zipfile.ZipFile("visuals.zip", 'r') as zf:
            zf.extractall(extract_dir)
    except Exception as e:
        print(f"C1: visuals.zip is invalid: {e}")
        return False
        
    ok, msg = check_artifact(extract_dir)
    if not ok:
        print(f"C2/C3 Failed: {msg}")
        return False
    else:
        print("C2: Backgrounds match expected count and 1280x720 size")
        print("C3: Character transparent cutouts found")
        
    print("Checking C4 (Style)...")
    ok, msg = check_style(extract_dir)
    if not ok:
        print(f"C4 Failed: {msg}")
        return False
    print(f"C4: Style is consistent and correct. Judge output: {msg}")
    
    print("VERDICT: PASS")
    return True

if __name__ == "__main__":
    if not run_fault_proof():
        sys.exit(1)
    if not verify_real():
        sys.exit(1)
