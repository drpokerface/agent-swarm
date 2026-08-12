import os, sys, zipfile, json, hashlib, random, shutil, subprocess
try:
    from PIL import Image
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "Pillow"])
    from PIL import Image

def sanitize(text):
    return hashlib.md5(text.encode('utf-8')).hexdigest()

def verify(zip_path, script_path, extract_dir):
    os.makedirs(extract_dir, exist_ok=True)
    res = {}
    
    # C1: valid zip
    if not os.path.exists(zip_path):
        res["C1"] = (False, f"{zip_path} missing")
    else:
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(extract_dir)
            res["C1"] = (True, "Valid zip")
        except Exception as e:
            res["C1"] = (False, f"Bad zip: {e}")
            
    if not res.get("C1", (False,))[0]:
        return res

    # C2: backgrounds
    with open(script_path, 'r') as f:
        script = json.load(f)
    bgs = set(s.get('background') for s in script if s.get('background'))
    
    c2_ok = True
    c2_msg = "Backgrounds OK"
    for bg in bgs:
        name = sanitize(bg) + ".png"
        path = os.path.join(extract_dir, "backgrounds", name)
        if not os.path.exists(path):
            c2_ok = False
            c2_msg = f"Missing bg {name}"
            break
        with Image.open(path) as img:
            if img.size != (1280, 720):
                c2_ok = False
                c2_msg = "Bad size"
                break
    res["C2"] = (c2_ok, c2_msg)
    
    # C3: characters
    chars = ["Brody", "Karen", "Sybil"]
    c3_ok = True
    c3_msg = "Chars OK"
    for char in chars:
        for state in ["silent", "talking"]:
            name = f"{char}_{state}.png"
            path = os.path.join(extract_dir, "characters", name)
            if not os.path.exists(path):
                c3_ok = False
                c3_msg = f"Missing char {name}"
                break
            with Image.open(path) as img:
                if img.mode != 'RGBA':
                    c3_ok = False
                    c3_msg = "Not RGBA"
                    break
    res["C3"] = (c3_ok, c3_msg)
    return res

def run():
    print("Running FAULT PROOFS...")
    os.makedirs("scratch/fp_test", exist_ok=True)
    with zipfile.ZipFile("scratch/fp_bad1.zip", "w") as z:
        z.writestr("backgrounds/missing.png", "fake")
    res = verify("scratch/fp_bad1.zip", "artifacts/issue-15/script.json", "scratch/fp_extract1")
    if not res.get("C2", (True,))[0] or not res.get("C1", (True,))[0]:
        print("FAULT-PROOF: C2 caught missing background correctly.")
    else:
        print("FAULT-PROOF: FAILED")
        return False
        
    print("VERIFYING ARTIFACT...")
    res = verify("visuals.zip", "artifacts/issue-15/script.json", "scratch/extract_final")
    all_pass = True
    for c, (ok, msg) in res.items():
        print(f"{c}: {msg}")
        if not ok: all_pass = False
        
    if all_pass:
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    run()
