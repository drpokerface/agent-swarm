# verify.py - Verify Audio Generation and Packaging
import os
import sys
import zipfile
import json
import shutil

def check_archive(zip_path, script_path):
    log_lines = []
    
    if not os.path.exists(zip_path):
        log_lines.append(f"C1: Fail - {zip_path} does not exist")
        return False, log_lines
        
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            namelist = z.namelist()
            log_lines.append(f"C1: Pass - {zip_path} is a valid zip archive")
            
            if 'timeline.json' not in namelist:
                log_lines.append("C2: Fail - timeline.json is missing in the archive")
                return False, log_lines
                
            timeline_content = z.read('timeline.json').decode('utf-8')
            timeline = json.loads(timeline_content)
            log_lines.append("C2: Pass - timeline.json exists and is valid JSON")
            
            if not isinstance(timeline, list):
                log_lines.append("C2: Fail - timeline.json must be a JSON array")
                return False, log_lines
                
            # C3: check referenced files exist in zip
            for entry in timeline:
                for key in ['dialogue_file', 'sfx_file', 'bgm_file']:
                    if key in entry and entry[key]:
                        if entry[key] not in namelist:
                            log_lines.append(f"C3: Fail - referenced file {entry[key]} not in zip")
                            return False, log_lines
            log_lines.append("C3: Pass - all referenced audio files exist in zip")
            
            # C5: check file sizes
            for fname in namelist:
                if fname.endswith('.mp3') or fname.endswith('.wav'):
                    if z.getinfo(fname).file_size < 100:
                        log_lines.append(f"C5: Fail - {fname} is too small")
                        return False, log_lines
            log_lines.append("C5: Pass - audio files are non-empty")
            
            # C6: SFX/music
            has_sfx = any(entry.get('sfx_file') for entry in timeline)
            has_bgm = any(entry.get('bgm_file') for entry in timeline)
            if not has_sfx or not has_bgm:
                log_lines.append(f"C6: Fail - timeline.json lacks SFX or BGM")
                return False, log_lines
            log_lines.append("C6: Pass - SFX and BGM are present")
            
    except Exception as e:
        log_lines.append(f"C1: Fail - exception reading zip: {e}")
        return False, log_lines
        
    return True, log_lines

def run_fault_proof(zip_path, script_path):
    os.makedirs('scratch', exist_ok=True)
    if not os.path.exists(zip_path):
        return False, "No zip to corrupt"
    
    scratch_zip = 'scratch/corrupted.zip'
    with zipfile.ZipFile(zip_path, 'r') as z_in, zipfile.ZipFile(scratch_zip, 'w') as z_out:
        for item in z_in.infolist():
            if item.filename == 'timeline.json':
                z_out.writestr(item, '{"invalid json')
            else:
                z_out.writestr(item, z_in.read(item.filename))
                
    success, logs = check_archive(scratch_zip, script_path)
    if success:
        return False, "Fault proof failed: check_archive passed a corrupted zip"
    return True, f"Caught fault: {logs[-1]}"

if __name__ == '__main__':
    zip_path = 'audio.zip'
    script_path = 'artifacts/issue-15/script.json'
    
    if os.path.exists(zip_path):
        fp_ok, fp_msg = run_fault_proof(zip_path, script_path)
        if not fp_ok:
            print("VERDICT: FAIL - Fault proof failed")
            sys.exit(1)
        print(f"FAULT-PROOF: {fp_msg}")
        
    success, logs = check_archive(zip_path, script_path)
    for line in logs:
        print(line)
        
    if success:
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)
