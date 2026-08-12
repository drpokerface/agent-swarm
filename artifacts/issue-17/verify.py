import os
import json
import re
import zipfile
from PIL import Image
import random
import shutil
import sys

def sanitize(text):
    return re.sub(r'[^a-z0-9]', '_', text.lower())[:50].strip('_')

def get_required_assets(script_path):
    with open(script_path, 'r') as f:
        script = json.load(f)
    bgs = set()
    chars = set()
    for scene in script:
        bg = scene.get('background', '')
        if bg: bgs.add(sanitize(bg))
        c_state = scene.get('character_state', '')
        if c_state and ':' in c_state:
            name, pose = c_state.split(':', 1)
            chars.add((sanitize(name), sanitize(pose)))
    return bgs, chars

def verify_zip(zip_path, script_path, quiet=False):
    if not os.path.exists(zip_path):
        if not quiet: print(f"FAIL: {zip_path} not found")
        return False
        
    bgs, chars = get_required_assets(script_path)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            files = set(zf.namelist())
            if not quiet: print(f"C1: ZIP exists - PASS (contains {len(files)} files)")
            
            for bg in bgs:
                expected = f"backgrounds/{bg}.png"
                if expected not in files:
                    if not quiet: print(f"FAIL: Missing {expected}")
                    return False
                with zf.open(expected) as f:
                    img = Image.open(f)
                    if img.size != (1280, 720):
                        if not quiet: print(f"FAIL: {expected} size is {img.size}")
                        return False
            if not quiet: print(f"C2: Backgrounds present and sized 1280x720 - PASS ({len(bgs)} backgrounds)")
                        
            for name, pose in chars:
                for state in ['closed', 'open']:
                    expected = f"characters/{name}/{pose}_{state}.png"
                    if expected not in files:
                        if not quiet: print(f"FAIL: Missing {expected}")
                        return False
                    with zf.open(expected) as f:
                        img = Image.open(f)
                        if img.mode not in ('RGBA', 'LA') and 'transparency' not in img.info:
                            if not quiet: print(f"FAIL: {expected} is not transparent PNG")
                            return False
            if not quiet: print(f"C3: Character states present and transparent - PASS ({len(chars)} poses)")
        return True
    except Exception as e:
        if not quiet: print(f"FAIL: exception reading zip: {e}")
        return False

if __name__ == "__main__":
    os.makedirs('scratch', exist_ok=True)
    fault_zip = 'scratch/fault_test.zip'
    if os.path.exists('visuals.zip'):
        shutil.copy('visuals.zip', fault_zip)
        with zipfile.ZipFile('visuals.zip', 'r') as zin:
            with zipfile.ZipFile(fault_zip, 'w') as zout:
                files = zin.namelist()
                pngs = [f for f in files if f.endswith('.png')]
                skip_file = random.choice(pngs) if pngs else None
                for item in zin.infolist():
                    if item.filename != skip_file:
                        zout.writestr(item, zin.read(item.filename))
        
        if not verify_zip(fault_zip, 'artifacts/issue-15/script.json', quiet=True):
            print(f"FAULT-PROOF: Caught missing file {skip_file} correctly")
        else:
            print("FAULT-PROOF FAILED")
            sys.exit(1)
            
    if verify_zip('visuals.zip', 'artifacts/issue-15/script.json'):
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)
