import os
import sys
import subprocess
import json
import shutil

try:
    from google import genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai"])
    from google import genai

def check_c1(d):
    try:
        t = open(os.path.join(d, "manifest.md"), encoding="utf-8").read()
        required = ["Filename", "Format", "Sample", "Description"]
        return all(r in t for r in required)
    except Exception:
        return False

def check_c2(d):
    try:
        t = open(os.path.join(d, "constitution.md"), encoding="utf-8").read()
        sections = ["Philosophy", "Strategy", "Style", "Conventions"]
        return all(s in t for s in sections)
    except Exception:
        return False

def check_c3(d):
    try:
        t = open(os.path.join(d, "constitution.md"), encoding="utf-8").read()
        return "threshold of 7" in t and "4:" in t and "7:" in t and "9:" in t
    except Exception:
        return False

def check_c4(d):
    try:
        t = open(os.path.join(d, "constitution.md"), encoding="utf-8").read()
        client = genai.Client()
        prompt = (
            "Evaluate this animation constitution on clarity, specificity, and alignment with the requested comedic style "
            "(Family Guy / South Park). Score it from 0 to 10. "
            'Reply with a JSON object: {"score": <number>}.\n\n' + t
        )
        resp = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=prompt,
            config={
                "response_mime_type": "application/json",
                "response_schema": {
                    "type": "object",
                    "properties": {"score": {"type": "number"}},
                    "required": ["score"]
                }
            }
        ).text
        data = json.loads(resp)
        score = float(data.get("score", 0))
        return score >= 7
    except Exception as e:
        print(f"Perceptual check failed: {e}")
        return False

def run_checks(d):
    return check_c1(d), check_c2(d), check_c3(d), check_c4(d)

def run_fault_proof():
    print("Running FAULT-PROOFS...")
    os.makedirs("scratch/faults", exist_ok=True)
    
    with open("scratch/faults/manifest.md", "w", encoding="utf-8") as f:
        f.write("Filename: app.py\nFormat: .py\nSample: code")
    if check_c1("scratch/faults"):
        print("FAULT-PROOF FAILED: C1 passed a manifest missing Description")
        sys.exit(1)
    else:
        print("FAULT-PROOF: C1 correctly caught manifest missing Description")
        
    with open("scratch/faults/constitution.md", "w", encoding="utf-8") as f:
        f.write("Philosophy\nStyle\nConventions\n")
    if check_c2("scratch/faults"):
        print("FAULT-PROOF FAILED: C2 passed a constitution missing Strategy")
        sys.exit(1)
    else:
        print("FAULT-PROOF: C2 correctly caught constitution missing Strategy")

    with open("scratch/faults/constitution.md", "w", encoding="utf-8") as f:
        f.write("Philosophy Strategy Style Conventions\n4: bad\n7: ok\n9: good\n")
    if check_c3("scratch/faults"):
        print("FAULT-PROOF FAILED: C3 passed a constitution missing threshold text")
        sys.exit(1)
    else:
        print("FAULT-PROOF: C3 correctly caught constitution missing threshold text")
        
    generic_filler = "Animation is a very important medium. It consists of many moving pictures. A good animation has characters. You need to make sure the frames go one after another. " * 50
    with open("scratch/faults/constitution.md", "w", encoding="utf-8") as f:
        f.write(generic_filler)
    
    if check_c4("scratch/faults"):
        print("FAULT-PROOF FAILED: C4 passed generic filler text")
        sys.exit(1)
    else:
        print("FAULT-PROOF: C4 correctly caught generic filler text and gave a low score")

def main():
    run_fault_proof()
    print("Running checks on actual workspace...")
    c1, c2, c3, c4 = run_checks(".")
    print(f"C1 (manifest.md): {c1}")
    print(f"C2 (sections): {c2}")
    print(f"C3 (rubric): {c3}")
    print(f"C4 (perceptual): {c4}")
    
    if all([c1, c2, c3, c4]):
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    main()
