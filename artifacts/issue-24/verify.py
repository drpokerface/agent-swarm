import os
import sys
import random
import string
import json
import subprocess

def install():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "-q"])

install()
from google import genai

def run_checks(filepath, is_fault_proof=False):
    if not os.path.exists(filepath):
        if not is_fault_proof: print("C1 (Exists): False")
        return False
    if not is_fault_proof: print("C1 (Exists): True")
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    content_lower = content.lower()
    
    if len(content.strip()) < 500:
        if not is_fault_proof: print("C2 (Degenerate - Length): False (Too short)")
        return False
        
    has_strategy = "strategy" in content_lower
    has_style = "style" in content_lower
    has_conv = "conventions" in content_lower
    has_manifest = "manifest.md" in content_lower
    c2 = has_strategy and has_style and has_conv and has_manifest
    if not is_fault_proof: print(f"C2 (Not Degenerate, structure present): {c2}")
    if not c2: return False
    
    has_4 = "4" in content_lower
    has_7 = "7" in content_lower
    has_9 = "9" in content_lower
    c3 = has_4 and has_7 and has_9
    if not is_fault_proof: print(f"C3 (Rubrics 4, 7, 9 present): {c3}")
    if not c3: return False
    
    has_todo = "todo" in content_lower or "[insert]" in content_lower or "placeholder" in content_lower or "lorem ipsum" in content_lower
    c4 = not has_todo
    if not is_fault_proof: print(f"C4 (No placeholders): {c4}")
    if not c4: return False
    
    if not is_fault_proof:
        try:
            client = genai.Client()
            prompt = "Score this adult animation goal constitution (0-10) against criteria: irreverent comedy, timing, pacing, 4/7/9 rubrics. Pass threshold is 7. Return JSON with 'score' (number) and 'reason'."
            resp = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[prompt, content],
                config={"response_mime_type": "application/json"}
            )
            data = json.loads(resp.text)
            score = float(data.get("score", 0))
            print(f"C6 (Score >= 7): {score} - {data.get('reason', '')}")
            if score < 7:
                return False
        except Exception as e:
            print(f"Model error: {e}")
            return False
            
    return True

if __name__ == '__main__':
    print("Running verify.py")
    
    main_file = "constitution.md"
    passed = run_checks(main_file, is_fault_proof=False)
    
    if not passed:
        print("VERDICT: FAIL")
        sys.exit(1)
        
    # Fault proof
    os.makedirs('scratch', exist_ok=True)
    fault_file = f"scratch/fault_{''.join(random.choices(string.digits, k=4))}.md"
    
    with open(main_file, 'r', encoding='utf-8') as f:
        content = f.read()
        
    # Inject placeholder to corrupt
    corrupted = content + "

TODO: finish this section"
    with open(fault_file, 'w', encoding='utf-8') as f:
        f.write(corrupted)
        
    print(f"Testing fault proof on {fault_file}...")
    fault_passed = not run_checks(fault_file, is_fault_proof=True)
    
    if not fault_passed:
        print("VERDICT: FAIL - Fault proof failed")
        sys.exit(1)
        
    print("FAULT-PROOF: Caught placeholder 'TODO' in scratch copy.")
    print("VERDICT: PASS")
    sys.exit(0)
