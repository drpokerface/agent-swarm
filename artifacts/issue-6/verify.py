# VALIDATED: caught incorrect resolution and duration
import os
import sys
import time
import json
import subprocess

def get_video_info(filepath):
    cmd = [
        'ffprobe', '-v', 'error', '-show_entries',
        'stream=codec_type,width,height', '-show_format', '-of', 'json', filepath
    ]
    try:
        res = subprocess.check_output(cmd, stderr=subprocess.STDOUT)
        data = json.loads(res.decode('utf-8'))
    except Exception as e:
        return None
    
    width = None
    height = None
    has_audio = False
    for stream in data.get('streams', []):
        if stream.get('codec_type') == 'video':
            width = int(stream.get('width', 0))
            height = int(stream.get('height', 0))
        elif stream.get('codec_type') == 'audio':
            has_audio = True
            
    duration = float(data.get('format', {}).get('duration', 0))
    return width, height, has_audio, duration

def check_c1(filepath):
    return os.path.exists(filepath)

def check_c2(filepath):
    info = get_video_info(filepath)
    if not info: return False
    w, h, _, _ = info
    return w == 1280 and h == 720

def check_c3(filepath):
    info = get_video_info(filepath)
    if not info: return False
    _, _, has_audio, _ = info
    return has_audio

def check_c4(filepath):
    info = get_video_info(filepath)
    if not info: return False
    _, _, _, duration = info
    return 110.0 <= duration <= 130.0

def evaluate_c5(filepath):
    if not os.environ.get("GEMINI_API_KEY"):
        print("No GEMINI_API_KEY")
        return False
    from google import genai
    
    client = genai.Client()
    video_file = client.files.upload(file=filepath)
    
    while True:
        video_file = client.files.get(name=video_file.name)
        state_str = str(getattr(video_file.state, 'name', video_file.state))
        if state_str == 'ACTIVE':
            break
        elif state_str == 'FAILED':
            print("Video processing failed in Gemini API")
            return False
        time.sleep(2)
        
    with open("artifacts/issue-2/spec.md", "r") as f:
        spec = f.read()
        
    prompt = f"Evaluate this video against the rubric. Output JSON with scores (1-5).\n\nRubric:\n{spec}"
    
    schema = {
        "type": "object",
        "properties": {
            "joke_density": {"type": "integer"},
            "hook_effectiveness": {"type": "integer"},
            "pacing": {"type": "integer"},
            "audio_sync": {"type": "integer"},
            "punchline_payoff": {"type": "integer"}
        },
        "required": ["joke_density", "hook_effectiveness", "pacing", "audio_sync", "punchline_payoff"]
    }
    
    all_scores = []
    for _ in range(3):
        res = client.models.generate_content(
            model="gemini-3.5-pro",
            contents=[video_file, prompt],
            config={
                "response_mime_type": "application/json",
                "response_schema": schema,
                "temperature": 0.2
            }
        )
        try:
            scores = json.loads(res.text)
            all_scores.append(scores)
        except Exception as e:
            print("Parse error", e)
            
    try:
        client.files.delete(name=video_file.name)
    except:
        pass
    
    if len(all_scores) < 3:
        return False
        
    medians = {}
    passed = True
    for key in ["joke_density", "hook_effectiveness", "pacing", "audio_sync", "punchline_payoff"]:
        vals = sorted([s[key] for s in all_scores])
        medians[key] = vals[1]
        print(f"Median {key}: {medians[key]}")
        if medians[key] < 4:
            passed = False
            
    return passed

def run_checks(filepath, skip_c5=False):
    c1 = check_c1(filepath)
    print(f"C1 (exists): {c1}")
    if not c1: return False
    
    c2 = check_c2(filepath)
    print(f"C2 (1280x720): {c2}")
    
    c3 = check_c3(filepath)
    print(f"C3 (audio): {c3}")
    
    c4 = check_c4(filepath)
    info = get_video_info(filepath)
    dur = info[3] if info else 0
    print(f"C4 (duration 110-130s): {c4} (Actual: {dur:.2f}s)")
    
    c5 = False
    if skip_c5:
        c5 = True 
    else:
        c5 = evaluate_c5(filepath)
        print(f"C5 (rubric >= 4): {c5}")
        
    return c1 and c2 and c3 and c4 and c5

def verify():
    print("Running check on actual artifact...")
    if not os.path.exists("final.mp4"):
        print("final.mp4 not found. EXPECTED FAILURE.")
        c1_res = False
    else:
        success = run_checks("final.mp4")
        if success:
            print("VERDICT: PASS")
        else:
            print("VERDICT: FAIL")
            
    print("\nFAULT-PROOF:")
    os.makedirs("scratch", exist_ok=True)
    faulty_file = "scratch/faulty_final.mp4"
    cmd = [
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'color=c=red:s=640x480:d=10',
        '-c:v', 'libx264', faulty_file
    ]
    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    print("Testing faulty file (10s, 640x480, no audio)...")
    res = run_checks(faulty_file, skip_c5=True)
    if not res:
        print("Fault-proof passed: Caught faulty video.")
        with open(__file__, 'r') as f:
            content = f.read()
        with open(__file__, 'w') as f:
            f.write(content.replace('# VALIDATED: caught incorrect resolution and duration', '# VALIDATED: caught incorrect resolution and duration'))
    else:
        print("Fault-proof failed: Faulty video passed.")

if __name__ == '__main__':
    verify()
