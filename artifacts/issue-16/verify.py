import os
import zipfile
import json

def verify(zip_path):
    if not os.path.exists(zip_path):
        return False, "C1: Missing"
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            files = z.namelist()
    except Exception as e:
        return False, f"C1: Invalid zip {e}"
        
    if 'timeline.json' not in files:
        return False, "C2: timeline.json missing"
        
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            data = z.read('timeline.json')
            timeline = json.loads(data)
    except Exception as e:
        return False, f"C2: timeline.json invalid {e}"
        
    for item in timeline:
        df = item.get('dialogue_file')
        sf = item.get('sfx_file')
        tf = item.get('file')
        if df and df not in files: return False, f"C3: missing {df}"
        if sf and sf not in files: return False, f"C3: missing {sf}"
        if tf and tf not in files: return False, f"C3: missing {tf}"
        
    return True, f"C1: ZIP OK | C2: JSON OK | C3: References OK (files={len(files)})"

def main():
    ok, msg = verify('audio.zip')
    print(msg)
    if not ok:
        print("VERDICT: FAIL")
        exit(1)
        
    os.makedirs('scratch/fault_verify', exist_ok=True)
    with zipfile.ZipFile('audio.zip', 'r') as z:
        z.extractall('scratch/fault_verify')
    with open('scratch/fault_verify/timeline.json', 'w') as f:
        f.write('invalid json')
    fault_zip = 'scratch/fault_audio.zip'
    with zipfile.ZipFile(fault_zip, 'w') as z:
        for root, dirs, files in os.walk('scratch/fault_verify'):
            for file in files:
                z.write(os.path.join(root, file), arcname=file)
                
    f_ok, f_msg = verify(fault_zip)
    if not f_ok:
        print(f"FAULT-PROOF: caught fault -> {f_msg}")
    
    print("VERDICT: PASS")

if __name__ == '__main__':
    main()
