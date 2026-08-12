import os
import sys
import json
import random
import shutil
import subprocess

try:
    from google import genai
    from google.genai import types
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai"])
    from google import genai
    from google.genai import types

SPEC_PATH = "artifacts/issue-7/spec.md"
SCRIPT_PATH = "script.json"

def check_c1(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            json.load(f)
        return True, "Valid JSON"
    except Exception as e:
        return False, f"Invalid JSON: {str(e)}"

def check_c2(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        if "scenes" not in data or not isinstance(data["scenes"], list):
            return False, "Missing or invalid 'scenes' array"
        if len(data["scenes"]) == 0:
            return False, "Empty scenes array"
        for s in data["scenes"]:
            if "background_prompt" not in s or not isinstance(s["background_prompt"], str):
                return False, "Missing or invalid 'background_prompt' in scene"
            if "dialogue" not in s or not isinstance(s["dialogue"], list):
                return False, "Missing or invalid 'dialogue' list in scene"
            if len(s["dialogue"]) == 0:
                return False, "Empty dialogue array"
            for d in s["dialogue"]:
                for k in ["character", "voice", "line", "visual_prompt"]:
                    if k not in d or not isinstance(d[k], str):
                        return False, f"Missing or invalid '{k}' in dialogue"
        return True, "Matches Schema"
    except Exception as e:
        return False, f"Schema error: {str(e)}"

def check_c3(filepath):
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
        words = 0
        for scene in data.get("scenes", []):
            for dial in scene.get("dialogue", []):
                words += len(str(dial.get("line", "")).split())
        if 250 <= words <= 350:
            return True, f"{words} words (within 250-350)"
        else:
            return False, f"{words} words (outside 250-350)"
    except Exception as e:
        return False, f"Count error: {str(e)}"

def check_c4(filepath):
    if not os.path.exists(SPEC_PATH):
        return False, "C4 Error: Spec missing"
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            script_data = f.read()
        with open(SPEC_PATH, "r", encoding="utf-8") as f:
            spec_data = f.read()
            
        client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        prompt = f"""You are an expert judge evaluating a script for a 2-minute original animated comedy short against its spec.
        
Spec:
{spec_data}

Script:
{script_data}

Evaluate if the script meets the criteria for pacing, humor, format, hook (in first 5s) and strong punchline at the end.
Provide integer scores from 1 to 10 for pacing, humor, and format.
Return ONLY valid JSON using exactly this schema:
{{
  "pacing": integer,
  "humor": integer,
  "format": integer,
  "feedback": "string"
}}
"""
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={
                    "type": "OBJECT",
                    "properties": {
                        "pacing": {"type": "INTEGER"},
                        "humor": {"type": "INTEGER"},
                        "format": {"type": "INTEGER"},
                        "feedback": {"type": "STRING"}
                    },
                    "required": ["pacing", "humor", "format", "feedback"]
                }
            )
        )
        
        try:
            result = json.loads(response.text)
        except json.JSONDecodeError as e:
            return False, f"C4 JSON Parse Error: {e}\nResponse was:\n{response.text}"
            
        pacing = result.get("pacing", 0)
        humor = result.get("humor", 0)
        format_score = result.get("format", 0)
        
        if pacing >= 7 and humor >= 7 and format_score >= 7:
            return True, f"Scores: pacing={pacing}, humor={humor}, format={format_score} (Pass)"
        else:
            return False, f"Scores: pacing={pacing}, humor={humor}, format={format_score} (Fail) Feedback: {result.get('feedback', '')}"
    except Exception as e:
        return False, f"C4 error: {str(e)}"

def run_checks():
    c1_ok, c1_msg = check_c1(SCRIPT_PATH)
    print(f"C1: {c1_msg}")
    c2_ok, c2_msg = check_c2(SCRIPT_PATH)
    print(f"C2: {c2_msg}")
    c3_ok, c3_msg = check_c3(SCRIPT_PATH)
    print(f"C3: {c3_msg}")
    
    # Fault proof
    os.makedirs("scratch", exist_ok=True)
    
    # Fault 1: Bad JSON
    with open("scratch/fault_bad_json.json", "w", encoding="utf-8") as f:
        f.write("{invalid")
    fc1_ok, fc1_msg = check_c1("scratch/fault_bad_json.json")
    
    # Fault 2: Empty scenes
    with open("scratch/fault_bad_schema.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({"scenes": []}))
    fc2_ok, fc2_msg = check_c2("scratch/fault_bad_schema.json")
    
    # Fault 3: Low Word Count
    with open("scratch/fault_bad_wc.json", "w", encoding="utf-8") as f:
        f.write(json.dumps({
            "scenes": [{"background_prompt": "bg", "dialogue": [{"character": "A", "voice": "V", "visual_prompt": "VP", "line": "Hi"}]}]
        }))
    fc3_ok, fc3_msg = check_c3("scratch/fault_bad_wc.json")
    
    fault_proofs = []
    fault_proofs.append(f"C1 caught bad JSON: {not fc1_ok} ({fc1_msg})")
    fault_proofs.append(f"C2 caught empty scenes: {not fc2_ok} ({fc2_msg})")
    fault_proofs.append(f"C3 caught low word count: {not fc3_ok} ({fc3_msg})")
    
    print(f"FAULT-PROOF: {'; '.join(fault_proofs)}")
    
    all_ok = c1_ok and c2_ok and c3_ok
    
    if all_ok:
        c4_ok, c4_msg = check_c4(SCRIPT_PATH)
        print(f"C4: {c4_msg}")
        if c4_ok:
            print("VERDICT: PASS")
            sys.exit(0)
        else:
            print("VERDICT: FAIL")
            sys.exit(1)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    run_checks()
