import os
import sys
import json
import random
import shutil

def check_script(filepath, skip_judge=False):
    if not os.path.exists(filepath):
        return False, "C1 fail: File does not exist"
    
    try:
        with open(filepath, 'r') as f:
            data = json.load(f)
    except Exception as e:
        return False, f"C1 fail: Invalid JSON - {e}"

    if not isinstance(data, dict) or "scenes" not in data or not isinstance(data["scenes"], list):
        return False, "C1 fail: Missing or invalid 'scenes' list or root structure"
        
    total_duration = 0
    total_words = 0
    hook_found = False
    punchline_found = False
    
    current_time = 0
    
    for i, scene in enumerate(data["scenes"]):
        if "duration_seconds" not in scene or not isinstance(scene["duration_seconds"], (int, float)):
            return False, f"C1 fail: Scene {i} missing/invalid 'duration_seconds'"
        if "dialogue" not in scene or not isinstance(scene["dialogue"], list):
            return False, f"C1 fail: Scene {i} missing/invalid 'dialogue'"
            
        dur = scene["duration_seconds"]
        
        for j, d in enumerate(scene["dialogue"]):
            for key in ["character", "voice", "line", "visual_prompt"]:
                if key not in d:
                    return False, f"C1 fail: Scene {i} dialogue {j} missing '{key}'"
            
            line_words = len(d["line"].split())
            total_words += line_words
            
            tag = d.get("tag")
            if tag == "hook" and current_time <= 5:
                hook_found = True
            if tag == "punchline":
                punchline_found = True
                
        current_time += dur
        total_duration += dur
        
    # Check C2 duration
    if abs(total_duration - 120.0) > 1e-4:
        return False, f"C2 fail: total duration {total_duration} != 120"
        
    # Check C3 word count
    if not (250 <= total_words <= 350):
        return False, f"C3 fail: total word count {total_words} not in [250, 350]"
        
    # Check C4 hook & punchline tags
    if not hook_found:
        return False, "C4 fail: hook tag not found in the first 5 seconds"
    if not punchline_found:
        return False, "C4 fail: punchline tag not found"
        
    if skip_judge:
        return True, f"Mechanical checks passed: duration={total_duration}s, words={total_words}"

    # C5 judging
    if "GEMINI_API_KEY" not in os.environ:
        return False, "C5 fail: GEMINI_API_KEY missing"
        
    try:
        from google import genai
    except ImportError:
        return False, "C5 fail: google-genai library missing"
        
    spec_path = "artifacts/issue-7/spec.md"
    if not os.path.exists(spec_path):
        return False, f"C5 fail: spec file {spec_path} not found"
        
    with open(spec_path) as f:
        spec = f.read()
        
    script_str = json.dumps(data, indent=2)
    prompt = f"""Evaluate this script against the spec. Beats lazy baseline (most obvious low-effort version)?
Return a JSON output matching the requested schema.

Spec:
{spec}

Script:
{script_str}
"""
    
    try:
        client = genai.Client()
        scores = []
        reasons = []
        beats_baselines = []
        for _ in range(3):
            res = client.models.generate_content(
                model="gemini-3.1-pro-preview",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": {
                        "type": "OBJECT",
                        "properties": {
                            "score": {"type": "INTEGER"},
                            "reasoning": {"type": "STRING"},
                            "beats_lazy_baseline": {"type": "BOOLEAN"}
                        },
                        "required": ["score", "reasoning", "beats_lazy_baseline"]
                    }
                }
            )
            ans = json.loads(res.text.strip())
            scores.append(ans["score"])
            reasons.append(ans["reasoning"])
            beats_baselines.append(ans["beats_lazy_baseline"])
            
        # Take median
        scores.sort()
        median_score = scores[1]
        beats_baseline = sum(beats_baselines) >= 2
        
        if median_score < 7:
            return False, f"C5 fail: median score is {median_score} < 7 (reasons: {reasons})"
        if not beats_baseline:
            return False, f"C5 fail: does not beat lazy baseline (reasons: {reasons})"
            
        return True, f"All claims pass! Median score: {median_score}, Beats baseline: {beats_baseline}"
    except Exception as e:
        return False, f"C5 error: failed calling Gemini Pro: {e}"

def induce_fault_and_verify():
    os.makedirs("scratch", exist_ok=True)
    # Generate a dummy script.json to corrupt
    dummy_data = {
        "scenes": [
            {
                "duration_seconds": 5,
                "dialogue": [
                    {
                        "character": "A",
                        "voice": "v1",
                        "line": "This is a hook line that should contain a good amount of words so that the total words are valid.",
                        "visual_prompt": "visual 1",
                        "tag": "hook"
                    }
                ]
            },
            {
                "duration_seconds": 115,
                "dialogue": [
                    {
                        "character": "B",
                        "voice": "v2",
                        "line": "We are adding a lot of words to reach the word count target. " * 25,
                        "visual_prompt": "visual 2",
                        "tag": "punchline"
                    }
                ]
            }
        ]
    }
    
    test_path = "scratch/test_fault.json"
    with open(test_path, "w") as f:
        json.dump(dummy_data, f, indent=2)
        
    # Test mechanical pass
    ok, msg = check_script(test_path, skip_judge=True)
    if not ok:
        return False, f"Dummy setup invalid: {msg}"
        
    # Random corruption
    corruption_type = random.choice(["duration", "word_count_low", "word_count_high", "hook_missing", "punchline_missing", "bad_json"])
    with open(test_path, "r") as f:
        corrupt_data = json.load(f)
        
    if corruption_type == "duration":
        corrupt_data["scenes"][0]["duration_seconds"] = 10  # total = 125
    elif corruption_type == "word_count_low":
        corrupt_data["scenes"][1]["dialogue"][0]["line"] = "Too short."
    elif corruption_type == "word_count_high":
        corrupt_data["scenes"][1]["dialogue"][0]["line"] = "Too long. " * 200
    elif corruption_type == "hook_missing":
        del corrupt_data["scenes"][0]["dialogue"][0]["tag"]
    elif corruption_type == "punchline_missing":
        del corrupt_data["scenes"][1]["dialogue"][0]["tag"]
    elif corruption_type == "bad_json":
        with open(test_path, "w") as f:
            f.write("{invalid json")
            
    if corruption_type != "bad_json":
        with open(test_path, "w") as f:
            json.dump(corrupt_data, f, indent=2)
            
    ok, msg = check_script(test_path, skip_judge=True)
    if not ok:
        # Clean up scratch
        try:
            os.remove(test_path)
        except:
            pass
        return True, f"Detected induced fault: {corruption_type} -> msg: {msg}"
    else:
        try:
            os.remove(test_path)
        except:
            pass
        return False, f"Failed to catch induced fault: {corruption_type}"

if __name__ == "__main__":
    # Run fault-proof first
    fp_ok, fp_msg = induce_fault_and_verify()
    if not fp_ok:
        print(f"FAULT-PROOF FAIL: {fp_msg}")
        sys.exit(1)
    print(f"FAULT-PROOF: {fp_msg}")
    
    real_script = "script.json"
    ok, msg = check_script(real_script, skip_judge=False)
    print(f"C1-C5 status: {msg}")
    if ok:
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)
