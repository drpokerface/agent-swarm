# verify.py - Validates script.json structure, duration, and rubric scores
import json
import os
import random
import shutil
import sys

# pip install google-genai pydantic
try:
    from google import genai
    from google.genai import types
except ImportError:
    import subprocess
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "pydantic"])
    from google import genai
    from google.genai import types

def check_c1_valid_json(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return True, "Valid JSON"
    except Exception as e:
        return False, str(e)

def check_c2_duration(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        scenes = data.get('scenes', [])
        if not scenes:
            return False, "No scenes"
        last_time = scenes[-1].get('end_time', 0)
        if 110 <= last_time <= 130:
            return True, f"Duration is {last_time}"
        else:
            return False, f"Duration is {last_time}, not in 110-130 range"
    except Exception as e:
        return False, str(e)

def check_c3_llm_eval(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            script_content = f.read()
        with open('artifacts/issue-2/spec.md', 'r', encoding='utf-8') as f:
            rubric = f.read()
            
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        prompt = f'''
Evaluate the following script.json content against the rubric provided.

RUBRIC:
{rubric}

SCRIPT CONTENT:
{script_content}

You must output exactly valid JSON with three keys: "Joke Density", "Hook Effectiveness", and "Punchline Payoff".
The value for each key must be an integer from 1 to 5 based on the rubric.
'''
        
        response = client.models.generate_content(
            model='gemini-3.5-flash',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "object",
                    "properties": {
                        "Joke Density": {"type": "integer"},
                        "Hook Effectiveness": {"type": "integer"},
                        "Punchline Payoff": {"type": "integer"}
                    },
                    "required": ["Joke Density", "Hook Effectiveness", "Punchline Payoff"]
                }
            )
        )
        
        res_json = json.loads(response.text)
        scores = [res_json.get("Joke Density", 0), res_json.get("Hook Effectiveness", 0), res_json.get("Punchline Payoff", 0)]
        if all(s >= 4 for s in scores):
            return True, f"Scores passing: {res_json}"
        else:
            return False, f"Scores failing: {res_json}"
    except Exception as e:
        return False, f"LLM error: {e}"

if __name__ == '__main__':
    print("\n--- FAULT PROOFS ---")
    os.makedirs('scratch', exist_ok=True)
    rand_id = random.randint(10000, 99999)
    
    # Fault 1: Invalid JSON
    fault1 = f"scratch/fault1_{rand_id}.json"
    with open(fault1, 'w') as f:
        f.write("{ invalid json")
    ok1, msg1 = check_c1_valid_json(fault1)
    if not ok1:
        print(f"FAULT-PROOF: C1 caught invalid JSON. Msg: {msg1}")
    else:
        print("FAULT-PROOF FAILED on C1")
        sys.exit(1)
        
    # Fault 2: Bad duration
    fault2 = f"scratch/fault2_{rand_id}.json"
    with open('script.json', 'r', encoding='utf-8') as f:
        d2 = json.load(f)
    if d2.get('scenes'):
        d2['scenes'][-1]['end_time'] = 50.0
    with open(fault2, 'w') as f:
        json.dump(d2, f)
    ok2, msg2 = check_c2_duration(fault2)
    if not ok2:
        print(f"FAULT-PROOF: C2 caught bad duration. Msg: {msg2}")
    else:
        print("FAULT-PROOF FAILED on C2")
        sys.exit(1)
        
    # Fault 3: Bad Content for LLM
    fault3 = f"scratch/fault3_{rand_id}.json"
    bad_data = {
        "title": "Boring",
        "characters": [],
        "scenes": [{
            "id": 1,
            "end_time": 120.0,
            "dialogue": [{"speaker": "A", "text": "Hello."}],
            "jokes": []
        }]
    }
    with open(fault3, 'w') as f:
        json.dump(bad_data, f)
    ok3, msg3 = check_c3_llm_eval(fault3)
    if not ok3:
        print(f"FAULT-PROOF: C3 caught low scores. Msg: {msg3}")
    else:
        print("FAULT-PROOF FAILED on C3")
        sys.exit(1)

    print("\n--- REAL CHECKS ---")
    target = "script.json"
    
    ok1, msg1 = check_c1_valid_json(target)
    print(f"C1 (Valid JSON): {msg1}")
    if not ok1: sys.exit(1)
    
    ok2, msg2 = check_c2_duration(target)
    print(f"C2 (Duration 110-130s): {msg2}")
    if not ok2: sys.exit(1)
    
    ok3, msg3 = check_c3_llm_eval(target)
    print(f"C3 (LLM Eval >= 4): {msg3}")
    if not ok3: sys.exit(1)
    
    print("VERDICT: PASS")
    sys.exit(0)
