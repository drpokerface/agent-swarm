# VERIFICATION SCRIPT FOR FINAL INTEGRATION
import os
import sys
import subprocess
import json
import random
import shutil

# Bootstrap dependencies
try:
    from google import genai
    from google.genai import types
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "pydantic"])
    from google import genai
    from google.genai import types

def run_ffprobe(filepath):
    cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filepath]
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except Exception:
        return None

def check_c1(target):
    return os.path.exists(target)

def check_c2(probe):
    if not probe: return False, "No probe data"
    for s in probe.get("streams", []):
        if s.get("codec_type") == "video":
            w = s.get("width")
            h = s.get("height")
            if w == 1280 and h == 720:
                return True, "1280x720"
            return False, f"{w}x{h}"
    return False, "No video stream"

def check_c3(probe):
    if not probe: return False, "No probe data"
    has_video = False
    has_audio = False
    for s in probe.get("streams", []):
        if s.get("codec_type") == "video": has_video = True
        if s.get("codec_type") == "audio": has_audio = True
    return has_video and has_audio, f"Video:{has_video} Audio:{has_audio}"

def check_c4(probe):
    if not probe: return False, "No probe data"
    fmt = probe.get("format", {})
    dur = float(fmt.get("duration", 0))
    if 100 <= dur <= 140:
        return True, f"{dur:.2f}s"
    return False, f"{dur:.2f}s"

def check_c5_perceptual(target):
    if not os.path.exists(target):
        return False, "File missing"
    if "GEMINI_API_KEY" not in os.environ:
        return False, "No API key"
    try:
        client = genai.Client()
        with open("rubric.md", "r") as f:
            rubric = f.read()
            
        print("Uploading to Gemini for perception check...", flush=True)
        vid_file = client.files.upload(file=target)
        
        prompt = "You are a judge evaluating a ~2 min animated comedy short. Review the video and this rubric:\n" + rubric + "\nIs it a cohesive animated comedy short with character voices, and does it score >= 7? Return JSON with boolean 'pass' and float 'score' and string 'reason'."
        
        response = client.models.generate_content(
            model="gemini-3.5-pro",
            contents=[vid_file, prompt],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema={"type": "object", "properties": {"pass": {"type": "boolean"}, "score": {"type": "number"}, "reason": {"type": "string"}}, "required": ["pass", "score", "reason"]}
            )
        )
        data = json.loads(response.text)
        client.files.delete(name=vid_file.name)
        
        return data.get("pass", False), f"Score: {data.get('score')} - {data.get('reason')}"
    except Exception as e:
        return False, f"API Error: {e}"

def run_fault_proof():
    print("\n--- FAULT-PROOF ---")
    os.makedirs('scratch', exist_ok=True)
    broken_path = 'scratch/broken.mp4'
    with open(broken_path, 'wb') as f:
        f.write(b'garbage data, not a video')
    
    probe = run_ffprobe(broken_path)
    if probe is None or not probe.get("streams"):
        print("FAULT-PROOF: Verified that verify.py catches an invalid video file.")
        return True
    return False

def main():
    print("--- CRITERIA CHECK ---")
    target = "final.mp4"
    
    c1 = check_c1(target)
    print(f"C1 (exists): {c1}")
    
    probe = run_ffprobe(target) if c1 else None
    
    c2, c2_val = check_c2(probe)
    print(f"C2 (1280x720): {c2} ({c2_val})")
    
    c3, c3_val = check_c3(probe)
    print(f"C3 (audio & video): {c3} ({c3_val})")
    
    c4, c4_val = check_c4(probe)
    print(f"C4 (~120s): {c4} ({c4_val})")
    
    # We only run perceptual if mechanical checks pass to save budget
    c5 = False
    c5_val = "Skipped"
    if c1 and c2 and c3 and c4:
        c5, c5_val = check_c5_perceptual(target)
    print(f"C5 (Perceptual >=7): {c5} ({c5_val})")
    
    fault_ok = run_fault_proof()
    
    if all([c1, c2, c3, c4, c5, fault_ok]):
        print("\nVERDICT: PASS")
        sys.exit(0)
    else:
        print("\nVERDICT: FAIL")
        sys.exit(1)

if __name__ == "__main__":
    main()
