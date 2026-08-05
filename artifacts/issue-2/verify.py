# VALIDATED: missing_dimension_and_scale
import os, sys, random

def verify_spec(path):
    if not os.path.exists(path):
        return False, "File does not exist"
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    required_dims = ["Joke Density", "Hook Effectiveness", "Pacing/Dead Air", "Audio Sync", "Punchline Payoff"]
    for dim in required_dims:
        if dim not in content:
            return False, f"Missing dimension: {dim}"
        dim_idx = content.find(dim)
        chunk = content[dim_idx:dim_idx+800]
        for scale in ["1:", "2:", "3:", "4:", "5:"]:
            if scale not in chunk:
                return False, f"Missing scale {scale} for {dim}"
                
    return True, "Has 5 dimensions and 1-5 scales"

if __name__ == '__main__':
    ok, msg = verify_spec("spec.md")
    
    print(f"Criterion 1 (spec.md exists): {os.path.exists('spec.md')}")
    print(f"Criterion 2 (5 dimensions and 1-5 scale): {msg}")
    
    os.makedirs("scratch", exist_ok=True)
    rand_id = random.randint(10000, 99999)
    scratch_path = f"scratch/fault_spec_{rand_id}.md"
    
    with open("spec.md", "r", encoding="utf-8") as f:
        good_content = f.read()
        
    bad_content = good_content.replace("3:", "THREE:")
    with open(scratch_path, "w", encoding="utf-8") as f:
        f.write(bad_content)
        
    fault_ok, fault_msg = verify_spec(scratch_path)
    if fault_ok:
        print("FAULT-PROOF FAILED: Did not catch missing scale.")
        sys.exit(1)
        
    print(f"FAULT-PROOF: verify_spec correctly caught fault on scratch copy - {fault_msg}")
    
    if not ok:
        print(f"FAILED: {msg}")
        sys.exit(1)
        
    print("VERDICT: PASS")
