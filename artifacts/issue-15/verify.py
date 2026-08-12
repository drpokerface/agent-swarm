#!/usr/bin/env python3
import json
import os
import sys
import copy
from google import genai

print('EXPECT: verify.py executing and demonstrating fault-proof.')

os.makedirs('scratch', exist_ok=True)

def test_fault(name, fault_func):
    try:
        with open('script.json', 'r') as f:
            data = json.load(f)
    except Exception:
        return
    faulty_data = fault_func(copy.deepcopy(data))
    fault_path = f'scratch/script_fault_{name}.json'
    with open(fault_path, 'w') as f:
        json.dump(faulty_data, f)
    
    try:
        check_all(fault_path, is_fault_test=True)
        print(f'FAULT-PROOF: {name} -> caught: False')
        sys.exit(1)
    except Exception as e:
        print(f'FAULT-PROOF: {name} -> caught: True (FAIL - {str(e)})')

def check_all(path, is_fault_test=False):
    with open(path, 'r') as f:
        data = json.load(f)
    
    if not isinstance(data, list) or len(data) == 0:
        raise Exception("Not a valid JSON list")
    
    total_dur = sum(float(shot.get('duration', 0)) for shot in data)
    if not (110 <= total_dur <= 130):
        raise Exception(f"Duration {total_dur} is not in [110, 130]")
    
    hook_found = False
    acc = 0
    for shot in data:
        if shot.get('hook'):
            if acc <= 5: hook_found = True
            break
        acc += float(shot.get('duration', 0))
    if not hook_found:
        raise Exception("no hook flagged true within first 5 seconds")
        
    for i, shot in enumerate(data):
        if not shot.get('dialogue', '').strip() and 'static' in shot.get('visual_state', '').lower():
            raise Exception(f"dead air in shot {i}")
            
    for i, shot in enumerate(data):
        for k in ['character', 'dialogue', 'visual_state', 'background', 'duration']:
            if k not in shot: raise Exception(f"shot {i} missing field {k}")
                
    if not data[-1].get('punchline'):
        raise Exception("Missing punchline payoff at the end")

    if not is_fault_test:
        print(f"C1 (Valid JSON List): Counted {len(data)} shots")
        print(f"C2 (Duration 110-130s): {total_dur:.2f}s")
        print(f"C3 (Hook <= 5s): Found=True")
        print("C4 (No Dead Air): No static silence >1s found")
        print("C5 (Visual/Audio prompts): All required keys present in all shots")
        print("C7 (Punchline payoff): Found=True")

        client = genai.Client(api_key=os.environ.get('GEMINI_API_KEY'))
        rubric = 'Score 1 to 10 on adult comedy style. MUST have clear punchline payoff at end. If it lacks a punchline, score 1. Return ONLY integer.'
        scores = []
        for _ in range(3):
            try:
                resp = client.models.generate_content(
                    model='gemini-2.5-pro',
                    contents=[rubric, json.dumps(data)]
                )
                score = int(resp.text.strip())
                scores.append(score)
            except Exception:
                scores.append(1)
        scores.sort()
        median = scores[1] if len(scores) == 3 else 1
        
        if median < 7:
            raise Exception(f"Median score {median} < 7. Fails comedy style.")
        print(f"C6 (Adult Comedy Style): Median score {median} >= 7")

def f_c2(d): d.append({"character":"A","dialogue":"B","visual_state":"C","background":"D","duration":1000}); return d
def f_c3(d): 
    for s in d:
        if 'hook' in s: del s['hook']
    return d
def f_c4(d): d.insert(0, {"character":"A","dialogue":"","visual_state":"static","background":"D","duration":5}); return d
def f_c5(d): del d[0]['duration']; return d
def f_c7(d):
    if 'punchline' in d[-1]: del d[-1]['punchline']
    return d

test_fault('C2_duration', f_c2)
test_fault('C3_hook', f_c3)
test_fault('C4_dead_air', f_c4)
test_fault('C5_missing_key', f_c5)
test_fault('C7_punchline', f_c7)

try:
    check_all('script.json', is_fault_test=False)
    print('VERDICT: PASS')
except Exception as e:
    print(f'VERDICT: FAIL - {e}')
    sys.exit(1)
