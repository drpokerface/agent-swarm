import os, sys, json, random, shutil
from google import genai

def run_checks(script_path, manifest_path):
    out = []
    
    # C1
    try:
        with open(script_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        if not isinstance(data, list):
            return False, out, "C1 error: Not a list"
        out.append(f"C1: valid JSON array of length {len(data)}")
    except Exception as e:
        return False, out, f"C1 error: {e}"

    # C2
    if not os.path.exists(manifest_path):
        return False, out, "C2 error: manifest.md missing"
    out.append(f"C2: manifest.md exists, size {os.path.getsize(manifest_path)}")

    # C3
    total_dur = sum(float(s.get('estimated_duration', s.get('duration', 0))) for s in data)
    out.append(f"C3: total duration is {total_dur}s")
    if total_dur < 100: 
        return False, out, f"C3 error: duration < 100 (is {total_dur})"

    # C4
    cutaways = sum(1 for s in data if 'cutaway' in json.dumps(s).lower())
    out.append(f"C4: cutaways count is {cutaways}")
    if cutaways < 2: 
        return False, out, f"C4 error: < 2 cutaways (is {cutaways})"

    # C5 & C6: Model call
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
    sample = json.dumps(data, indent=2)
    with open('artifacts/issue-19/constitution.md', 'r', encoding='utf-8') as f:
        constitution = f.read()

    prompt = f"""Constitution:
{constitution}

Script:
{sample[:15000]}

Evaluate this script.
1. Is it a comedic script with dialogue and visual prompts?
2. Score it from 0 to 10 on humor and pacing against the constitution (Pass threshold: 7)."""
    
    schema = {
        "type": "object",
        "properties": {
            "is_comedic_script": {"type": "boolean"},
            "has_dialogue_and_visuals": {"type": "boolean"},
            "score": {"type": "number"},
            "justification": {"type": "string"}
        },
        "required": ["is_comedic_script", "has_dialogue_and_visuals", "score", "justification"]
    }
    try:
        resp = client.models.generate_content(
            model="gemini-3.5-flash", 
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": 0.0
            }
        ).text
        result = json.loads(resp)
        
        out.append(f"C5: is_comedic={result['is_comedic_script']}, has_dialogue_and_visuals={result['has_dialogue_and_visuals']}")
        if not (result['is_comedic_script'] and result['has_dialogue_and_visuals']):
            return False, out, "C5 error: not perceived as a comedic script with dialogue and visuals"

        out.append(f"C6: score is {result['score']} - {result['justification']}")
        if result['score'] < 7:
            return False, out, f"C6 error: score {result['score']} < 7"
            
    except Exception as e:
        return False, out, f"C5/C6 model call error: {e}"

    return True, out, "All criteria passed."

def main():
    print("Running verify.py checks...")
    ok, lines, msg = run_checks('script.json', 'manifest.md')
    for line in lines:
        print(line)
        
    if not ok:
        print(f"FAILED: {msg}")
        sys.exit(1)

    # FAULT PROOF
    print("Running FAULT-PROOF...")
    os.makedirs('scratch', exist_ok=True)
    bad_script_path = f"scratch/corrupted_script_{random.randint(1000, 9999)}.json"
    
    with open('script.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        
    # Corrupt duration to fail C3
    for s in data:
        if 'estimated_duration' in s:
            s['estimated_duration'] = 1
        if 'duration' in s:
            s['duration'] = 1
            
    with open(bad_script_path, 'w', encoding='utf-8') as f:
        json.dump(data, f)
        
    ok, f_lines, f_msg = run_checks(bad_script_path, 'manifest.md')
    if ok:
        print("FAILED FAULT-PROOF: Checks passed on corrupted script!")
        sys.exit(1)
        
    print(f"FAULT-PROOF: Caught induced fault correctly ({f_msg})")
    print("VERDICT: PASS")
    sys.exit(0)

if __name__ == '__main__':
    main()