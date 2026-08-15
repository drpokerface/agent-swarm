# verify.py - Validation suite for constitution_bundle.zip
import os
import zipfile
import shutil
import random
import re
import sys
import subprocess
import json

try:
    from google import genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "pydantic"])
    from google import genai

def verify(filepath, is_fault_run=False):
    claims = {}
    
    # C1: zip exists
    c1 = os.path.exists(filepath)
    claims['C1'] = f"Exists: {c1}"
    if not c1:
        return False, claims, "C1 failed"

    # C2: decodes & C3: contains files
    try:
        with zipfile.ZipFile(filepath, 'r') as z:
            namelist = z.namelist()
            c3 = set(namelist) == {'constitution.md', 'manifest.md'}
            claims['C3'] = f"Files in zip: {namelist}"
            if not c3: return False, claims, "C3 failed"

            const_bytes = z.read('constitution.md')
            man_bytes = z.read('manifest.md')
            const_text = const_bytes.decode('utf-8')
            man_text = man_bytes.decode('utf-8')
            claims['C2'] = "Decodes correctly: True"
    except Exception as e:
        claims['C2'] = f"Decodes correctly: False ({e})"
        return False, claims, "C2 failed"
        
    # C4: Word count > 500
    words = len(const_text.split()) + len(man_text.split())
    claims['C4'] = f"Combined word count: {words}"
    if words <= 500: return False, claims, "C4 failed"

    # C8: No placeholders/degeneracy
    placeholders = ['todo', 'tbd', 'lorem ipsum', '[insert', '<insert', 'placeholder']
    has_ph = [p for p in placeholders if p in const_text.lower() or p in man_text.lower()]
    claims['C8'] = f"Placeholders found: {has_ph}"
    if has_ph: return False, claims, "C8 failed"

    if len(const_text.strip()) == 0 or len(set(const_text)) < 20:
        return False, claims, "C8 failed: degenerate uniform text"

    # C5: Sections exist
    sections = ['strategy', 'style decisions', 'conventions', 'scoring rubric']
    missing_sec = [sec for sec in sections if sec not in const_text.lower()]
    claims['C5'] = f"Missing sections: {missing_sec}"
    if missing_sec: return False, claims, "C5 failed"

    # C6: Rubric anchors
    anchors = ['4', '7', '9']
    missing_anchors = [a for a in anchors if a not in const_text]
    claims['C6'] = f"Missing anchors: {missing_anchors}"
    if missing_anchors: return False, claims, "C6 failed"

    # C7: manifest.md formats
    has_manifest = 'constitution.md' in man_text and 'manifest.md' in man_text
    claims['C7'] = f"Manifest valid contents: {has_manifest}"
    if not has_manifest: return False, claims, "C7 failed"

    # C9: LLM Score
    if is_fault_run:
        claims['C9'] = "Skipped for fault run"
    else:
        try:
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY", ""))
            prompt = f"""Evaluate the following adult animation comedy constitution against this quality criteria:
- Must be fast-paced, irreverent, South Park/Family Guy style.
- Must provide anchored rubrics for humor, pacing, visual cohesion, audio sync.
- Score from 0 to 10. Threshold is 7.0.
Constitution Content:
{const_text}
"""
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=prompt,
                config={"response_mime_type": "application/json", "response_schema": {"type": "object", "properties": {"score": {"type": "number"}, "justification": {"type": "string"}}, "required": ["score", "justification"]}}
            )
            
            try:
                text_val = response.text
            except Exception:
                text_val = "{}"
            try:
                res = json.loads(text_val)
            except Exception:
                score_match = re.search(r'"score"\s*:\s*([\d\.]+)', text_val)
                res = {"score": float(score_match.group(1)) if score_match else 0.0, "justification": "Fallback"}
                
            score = float(res.get("score", 0.0))
            claims['C9'] = f"Score: {score} | Justification: {res.get('justification')}"
            if score < 7.0: return False, claims, "C9 failed"
        except Exception as e:
            claims['C9'] = f"LLM error: {e}"
            return False, claims, "C9 failed"

    return True, claims, "Pass"

def main():
    print("EXPECT: Validate constitution_bundle.zip")
    os.makedirs('scratch', exist_ok=True)
    
    # Fault proof
    fault_path = f"scratch/fault_{random.randint(10000, 99999)}.zip"
    shutil.copy('constitution_bundle.zip', fault_path)
    with open(fault_path, 'r+b') as f:
        f.seek(0)
        f.write(b'GARBAGE' * 20)
        
    try:
        ok, fclaims, fmsg = verify(fault_path, is_fault_run=True)
    except Exception as e:
        ok, fmsg = False, str(e)
        
    if not ok:
        print(f"FAULT-PROOF: Successfully caught corruption! {fmsg}")
    else:
        print("FAULT-PROOF: FAILED to catch corruption!")
        exit(1)
        
    ok, rclaims, rmsg = verify('constitution_bundle.zip')
    
    for c, val in sorted(rclaims.items()):
        print(f"{c} - {val}")
        
    if ok:
        print("VERDICT: PASS")
        exit(0)
    else:
        print(f"VERDICT: FAIL ({rmsg})")
        exit(1)

if __name__ == '__main__':
    main()