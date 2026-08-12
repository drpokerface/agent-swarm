# VERIFY PROGRAM
import os
import sys
import zipfile
import random
import shutil
import subprocess
import json

def install_deps():
    try:
        import PIL
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', 'pillow', '-q'])

install_deps()
from PIL import Image

def get_expected_files():
    with open('artifacts/issue-9/script.json', 'r') as f:
        data = json.load(f)
    expected = []
    for s_idx, scene in enumerate(data['scenes']):
        expected.append(f'scene_{s_idx}_background.png')
        for d_idx, dial in enumerate(scene.get('dialogue', [])):
            char_name = dial['character'].replace(' ', '_')
            expected.append(f'scene_{s_idx}_char_{d_idx}_{char_name}.png')
    return expected

def verify_zip(zip_path, extract_dir):
    if not os.path.exists(zip_path):
        return False, f'C1 FAIL: {zip_path} not found'
        
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extractall(extract_dir)
    except Exception as e:
        return False, f'C1 FAIL: Could not extract {zip_path} - {e}'

    expected_files = get_expected_files()
    
    for f in expected_files:
        p = os.path.join(extract_dir, f)
        if not os.path.exists(p):
            return False, f'C1 FAIL: Missing expected file {f}'
            
        try:
            with Image.open(p) as img:
                if img.format != 'PNG':
                    return False, f'C1/C2/C3 FAIL: {f} is not a PNG (format: {img.format})'
                
                if 'background' in f:
                    if img.size != (1280, 720):
                        return False, f'C2 FAIL: {f} is not 1280x720 (size: {img.size})'
                
                if 'char' in f:
                    has_alpha = False
                    if img.mode in ('RGBA', 'LA', 'PA'):
                        has_alpha = True
                    elif 'transparency' in img.info:
                        has_alpha = True
                    else:
                        has_alpha = any(band in ['A', 'a'] for band in img.getbands())
                        
                    if not has_alpha:
                        return False, f'C3 FAIL: {f} does not have a transparent background (mode: {img.mode})'
        except Exception as e:
            return False, f'FAIL: Error reading {f} - {e}'

    return True, 'C1, C2, C3 passed'

def build_mock_zip(path, corrupt_c2=False, corrupt_c3=False):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    extract_dir = path + '_mock'
    if os.path.exists(extract_dir):
        shutil.rmtree(extract_dir)
    os.makedirs(extract_dir, exist_ok=True)
    
    expected_files = get_expected_files()
    for f in expected_files:
        p = os.path.join(extract_dir, f)
        if 'background' in f:
            img = Image.new('RGB', (1280, 720), color = 'blue')
            img.save(p, 'PNG')
        else:
            img = Image.new('RGBA', (100, 100), color = (0, 255, 0, 128))
            img.save(p, 'PNG')

    # Inject faults deterministically
    if corrupt_c2:
        bg_files = [f for f in expected_files if 'background' in f]
        if bg_files:
            img = Image.new('RGB', (1000, 1000), color = 'red')
            img.save(os.path.join(extract_dir, bg_files[0]), 'PNG')
            
    if corrupt_c3:
        char_files = [f for f in expected_files if 'char' in f]
        if char_files:
            img = Image.new('RGB', (100, 100), color = 'green')
            img.save(os.path.join(extract_dir, char_files[0]), 'PNG')

    with zipfile.ZipFile(path, 'w') as z:
        for f in os.listdir(extract_dir):
            z.write(os.path.join(extract_dir, f), f)
            
    shutil.rmtree(extract_dir)

def run_fault_proofs():
    print('Running fault proofs...')
    mock_path = 'scratch/mock_visuals.zip'
    extract_dir = 'scratch/verify_extract_mock'
    
    build_mock_zip(mock_path, corrupt_c2=True)
    success, msg = verify_zip(mock_path, extract_dir)
    if success:
        print('FAULT-PROOF FAIL: Failed to catch C2 (size) corruption')
        sys.exit(1)
    else:
        print(f'FAULT-PROOF: Caught C2 fault: {msg}')

    build_mock_zip(mock_path, corrupt_c3=True)
    success, msg = verify_zip(mock_path, extract_dir)
    if success:
        print('FAULT-PROOF FAIL: Failed to catch C3 (transparency) corruption')
        sys.exit(1)
    else:
        print(f'FAULT-PROOF: Caught C3 fault: {msg}')
        
    print('Fault proofs passed.')

if __name__ == '__main__':
    run_fault_proofs()
    
    success, msg = verify_zip('visuals.zip', 'scratch/verify_extract_real')
    print(msg)
    if success:
        print('VERDICT: PASS')
        sys.exit(0)
    else:
        sys.exit(1)
