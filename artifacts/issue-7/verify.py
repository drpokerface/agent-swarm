# verify.py - executable verification rollup for spec.md
import os
import random
import sys

def verify_spec(filepath):
    if not os.path.exists(filepath):
        return False, "C1: Missing"
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if not content.strip():
        return False, "C1: Empty"

    if "Measurable Properties" not in content or "Pacing" not in content or "Joke Density" not in content or "Tone" not in content:
        return False, "C2: Missing measurable properties"
    
    rubric_sections = ["Pacing", "Joke Density", "Visual Clarity", "Shared Spec"]
    for section in rubric_sections:
        if section not in content:
            return False, f"C4: Missing rubric section {section}"
            
    for i in range(1, 6):
        if f"{i}:" not in content:
            return False, f"C3: Missing score {i}:"
            
    for spec_detail in ["2-minute", "MP4", "1280x720"]:
        if spec_detail not in content:
             return False, f"C4: Missing shared spec detail: {spec_detail}"
    
    if "Anchor:" not in content:
        return False, "C5: Missing anchors"
        
    return True, "PASS"

if __name__ == "__main__":
    ok, msg = verify_spec('spec.md')
    if not ok:
        print(f"FAILED: {msg}")
        sys.exit(1)
        
    print("C1: spec.md exists: True")
    print("C2: measurable properties: True")
    print("C3: 1-5 scoring rubric: True")
    print("C4: rubric dimensions: True")
    print("C5: anchored descriptors: True")
    
    os.makedirs('scratch', exist_ok=True)
    bad_path = f'scratch/fault_spec_{random.randint(1000, 99999)}.md'
    with open('spec.md', 'r', encoding='utf-8') as f:
        good = f.read()
    with open(bad_path, 'w', encoding='utf-8') as f:
        f.write(good.replace("Anchor:", "None:"))
        
    ok, msg = verify_spec(bad_path)
    if not ok:
        print(f"FAULT-PROOF: Caught missing anchors on {bad_path} ({msg})")
    else:
        print("FAULT-PROOF FAILED")
        sys.exit(1)
        
    print("VERDICT: PASS")
