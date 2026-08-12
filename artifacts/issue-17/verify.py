# verify.py - Validates visuals.zip against criteria.md
import os
import sys
import zipfile
import json
import tempfile
import shutil

def log_criterion(name, value, passed):
    status = 'PASS' if passed else 'FAIL'
    print(f'{name}: {value} ({status})')

def run_checks(zip_path):
    # Recompute every claim from disk
    if not os.path.exists(zip_path):
        return False, f'{zip_path} not found'
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            namelist = z.namelist()
    except Exception as e:
        return False, f'Invalid zip: {e}'
        
    # Load script
    script_path = 'artifacts/issue-15/script.json'
    if not os.path.exists(script_path):
        return False, f'{script_path} not found'
        
    with open(script_path, 'r') as f:
        data = json.load(f)
        
    unique_bgs = set(item.get('background') for item in data if item.get('background'))
    unique_chars_states = set()
    for item in data:
        char = item.get('character')
        state = item.get('character_state')
        if char and state:
            unique_chars_states.add((char, state))
        elif char:
            unique_chars_states.add((char, 'default'))
            
    # Let's map backgrounds to filenames: let's define a sanitization rule for names
    # Let's use lower case alphanumeric with underscores
    def sanitize(text):
        import re
        return re.sub(r'[^a-z0-9_]', '_', text.lower().strip())
        
    # Check C2: Backgrounds
    bg_missing = []
    for bg in unique_bgs:
        expected_name = f'backgrounds/{sanitize(bg)}.png'
        if expected_name not in namelist:
            bg_missing.append(expected_name)
            
    # Check C3: Characters with mouth_open and mouth_closed states
    char_missing = []
    for char, state in unique_chars_states:
        for suffix in ['_mouth_open.png', '_mouth_closed.png']:
            expected_name = f'characters/{sanitize(char)}_{sanitize(state)}{suffix}'
            if expected_name not in namelist:
                char_missing.append(expected_name)
                
    passed = len(bg_missing) == 0 and len(char_missing) == 0
    details = f'Missing BGs: {len(bg_missing)}, Missing Chars: {len(char_missing)}'
    if not passed:
        if bg_missing:
            details += f' | Sample missing BG: {bg_missing[0]}'
        if char_missing:
            details += f' | Sample missing Char: {char_missing[0]}'
    return passed, details

if __name__ == '__main__':
    # Main verification
    zip_path = 'visuals.zip'
    real_passed, real_details = run_checks(zip_path)
    
    log_criterion('C1: visuals.zip exists', os.path.exists(zip_path), os.path.exists(zip_path))
    log_criterion('C2: All backgrounds represented', real_passed, real_passed)
    log_criterion('C3: All character states with mouth open/closed represented', real_passed, real_passed)
    
    # FAULT-PROOF: corrupt a COPY at a random site under scratch/
    os.makedirs('scratch', exist_ok=True)
    scratch_zip = 'scratch/corrupted_visuals.zip'
    
    # Create a test zip if the real one exists to corrupt it, otherwise let's simulate corruption
    if os.path.exists(zip_path):
        # We copy, unpack, remove one random file, repack, and run checks
        temp_dir = tempfile.mkdtemp(dir='scratch')
        try:
            with zipfile.ZipFile(zip_path, 'r') as z:
                z.extractall(temp_dir)
            # Find all files
            all_files = []
            for root, dirs, files in os.walk(temp_dir):
                for f in files:
                    all_files.append(os.path.join(root, f))
            if all_files:
                import random
                corrupt_target = random.choice(all_files)
                os.remove(corrupt_target)
                # Repack
                with zipfile.ZipFile(scratch_zip, 'w') as sz:
                    for root, dirs, files in os.walk(temp_dir):
                        for f in files:
                            full_path = os.path.join(root, f)
                            arcname = os.path.relpath(full_path, temp_dir)
                            sz.write(full_path, arcname)
                # Run checks on corrupted zip
                corrupt_passed, corrupt_details = run_checks(scratch_zip)
                if not corrupt_passed:
                    print(f'FAULT-PROOF: Successfully caught induced fault! Corrupted file: {os.path.basename(corrupt_target)}')
                else:
                    print('FAULT-PROOF: FAILED to catch induced fault on corrupted zip!')
                    sys.exit(1)
            else:
                print('FAULT-PROOF: No files inside zip to corrupt!')
                sys.exit(1)
        finally:
            shutil.rmtree(temp_dir)
            if os.path.exists(scratch_zip):
                os.remove(scratch_zip)
    else:
        # Real zip doesn't exist yet, we can show fault-proof by running on a dummy empty zip
        dummy_zip = 'scratch/dummy.zip'
        with zipfile.ZipFile(dummy_zip, 'w') as z:
            z.writestr('dummy.txt', 'hello')
        corrupt_passed, corrupt_details = run_checks(dummy_zip)
        if not corrupt_passed:
            print('FAULT-PROOF: Successfully caught induced fault on empty zip!')
        else:
            print('FAULT-PROOF: FAILED to catch induced fault on empty zip!')
            sys.exit(1)
        os.remove(dummy_zip)
        
    if real_passed:
        print('VERDICT: PASS')
        sys.exit(0)
    else:
        print('VERDICT: FAIL (Real artifact checks failed or missing)')
        sys.exit(1)
