import json, os, random, shutil, sys

def measure(filepath):
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except Exception as e:
        return {"C1": f"Fail: JSON error {e}", "C2": "Fail", "C3": "Fail", "C4": "Fail", "C5": "Fail", "pass": False}
    
    if not isinstance(data, list) or len(data) == 0:
        return {"C1": "Fail: Not a non-empty list", "C2": "Fail", "C3": "Fail", "C4": "Fail", "C5": "Fail", "pass": False}
        
    results = {"C1": "Pass: Valid JSON array", "pass": True}
    
    total_duration = 0.0
    hook_found_early = False
    
    for idx, shot in enumerate(data):
        if not all(k in shot for k in ['background', 'dialogue', 'character_state', 'duration']):
            results["C5"] = f"Fail: Shot {idx} missing required keys"
            results["pass"] = False
            return results
        if not isinstance(shot['duration'], (int, float)) or shot['duration'] <= 0:
            results["C5"] = f"Fail: Shot {idx} invalid duration"
            results["pass"] = False
            return results
            
        if shot.get('is_hook') is True and total_duration <= 5.0:
            hook_found_early = True
            
        is_empty_dialogue = not shot.get('dialogue', '').strip()
        if is_empty_dialogue and shot['duration'] > 1.5:
            if not shot.get('visual_gag'):
                results["C4"] = f"Fail: Shot {idx} dead air without visual_gag"
                results["pass"] = False
                return results
                
        total_duration += shot['duration']
        
    results.setdefault("C5", "Pass: All shots have required keys")
    results.setdefault("C4", "Pass: No dead air")
    
    if 110 <= total_duration <= 130:
        results["C2"] = f"Pass: Duration {total_duration:.1f}s"
    else: 
        results["C2"] = f"Fail: Duration {total_duration:.1f}s not in 110-130s"
        results["pass"] = False
        
    if hook_found_early:
        results["C3"] = "Pass: Early hook found"
    else:
        results["C3"] = "Fail: No hook in first 5s"
        results["pass"] = False
        
    return results

def main():
    # 1. Run checks on real artifact
    res = measure('script.json')
    print(f"C1: {res.get('C1', 'Fail')}")
    print(f"C2: {res.get('C2', 'Fail')}")
    print(f"C3: {res.get('C3', 'Fail')}")
    print(f"C4: {res.get('C4', 'Fail')}")
    print(f"C5: {res.get('C5', 'Fail')}")
    
    if not res['pass']:
        print("VERDICT: FAIL - real artifact does not meet criteria")
        sys.exit(1)
        
    # 2. Fault-Proof: Corrupt a COPY of the artifact at a RANDOM site under scratch/
    os.makedirs('scratch', exist_ok=True)
    random_num = random.randint(1000, 9999)
    scratch_file = f'scratch/fault_{random_num}.json'
    shutil.copy('script.json', scratch_file)
    
    with open(scratch_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Apply a random fault
    fault_type = random.choice(['duration', 'dead_air', 'missing_key', 'no_hook'])
    if fault_type == 'duration':
        # change a duration to be extremely large
        if data:
            data[0]['duration'] = 1000.0
    elif fault_type == 'dead_air':
        # add empty dialogue with duration and no visual gag
        if data:
            data[0]['dialogue'] = ''
            data[0]['duration'] = 5.0
            if 'visual_gag' in data[0]:
                del data[0]['visual_gag']
    elif fault_type == 'missing_key':
        if data:
            if 'dialogue' in data[0]:
                del data[0]['dialogue']
    elif fault_type == 'no_hook':
        # remove all is_hook flags
        for shot in data:
            if 'is_hook' in shot:
                del shot['is_hook']
                
    with open(scratch_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2)
        
    # Measure the corrupted copy
    corrupt_res = measure(scratch_file)
    if corrupt_res['pass']:
        print(f"VERDICT: FAIL - failed to catch induced fault {fault_type}")
        sys.exit(1)
    else:
        # find which one failed
        failed_crit = [k for k, v in corrupt_res.items() if k != 'pass' and 'Fail' in v]
        print(f"FAULT-PROOF: Caught induced {fault_type} fault -> {corrupt_res}")
        
    print("VERDICT: PASS")

if __name__ == '__main__':
    main()