import os
import sys
import subprocess
import json
import time
import random
import shutil

# Ensure dependencies are available
try:
    import google.genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "-q"])

from google import genai

def get_media_info(filepath):
    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return None

def verify_file(filepath):
    if not os.path.exists(filepath):
        print(f"C1: FAIL - {filepath} does not exist")
        return False
    print(f"C1: PASS - {filepath} exists")

    info = get_media_info(filepath)
    if not info:
        print("C2-C4: FAIL - Could not parse media info")
        return False

    duration = float(info.get('format', {}).get('duration', 0))
    if 110 <= duration <= 140:
        print(f"C2: PASS - Duration is {duration}s")
    else:
        print(f"C2: FAIL - Duration is {duration}s (must be ~120s)")
        return False

    streams = info.get('streams', [])
    v_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
    a_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)

    if v_stream and a_stream:
        print("C4: PASS - AV streams present")
    else:
        print("C4: FAIL - Missing AV streams")
        return False

    width = int(v_stream.get('width', 0))
    height = int(v_stream.get('height', 0))
    if width == 1280 and height == 720:
        print(f"C3: PASS - Resolution is {width}x{height}")
    else:
        print(f"C3: FAIL - Resolution is {width}x{height} (must be 1280x720)")
        return False

    # Check content non-degeneracy & quality via Gemini API
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("C5/C6: FAIL - Missing GEMINI_API_KEY")
            return False
        client = genai.Client(api_key=api_key)
        video_file = client.files.upload(file=filepath)
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        if video_file.state.name == "FAILED":
            print("C5/C6: FAIL - Video upload/processing failed")
            return False

        rubric = """Evaluate this animated comedy short on Humor, Timing, and Cohesion (Family Guy/South Park style).
Also verify it contains character dialogue, music, sound effects, and has distinct active frames.
Rate the overall quality from 0 to 10 (Pass threshold is 7).
Return JSON format: {\"score\": 8, \"reasoning\": \"...\", \"is_degenerate\": false}"""
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[rubric, video_file],
            config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        client.files.delete(name=video_file.name)
        
        score = data.get("score", 0)
        is_degen = data.get("is_degenerate", True)
        if is_degen:
            print("C5: FAIL - Video determined to be degenerate")
            return False
        print("C5: PASS - Video is non-degenerate")
        
        if score >= 7:
            print(f"C6: PASS - Perception score {score} >= 7. Reasoning: {data.get('reasoning')}")
        else:
            print(f"C6: FAIL - Perception score {score} < 7. Reasoning: {data.get('reasoning')}")
            return False
    except Exception as e:
        print(f"C5/C6: FAIL - Perception check error: {e}")
        return False

    return True

if __name__ == '__main__':
    # Run a fault proof
    os.makedirs('scratch', exist_ok=True)
    fault_path = 'scratch/corrupted.mp4'
    with open(fault_path, 'wb') as f:
        f.write(os.urandom(1024))
    
    print("FAULT-PROOF: Testing verification routine with corrupt dummy file.")
    info = get_media_info(fault_path)
    if info is None:
        print("FAULT-PROOF SUCCESS: Corrupt dummy file correctly failed parse check.")
    else:
        print("FAULT-PROOF FAILURE: Corrupt file parsed successfully.")
        
    try:
        os.remove(fault_path)
    except:
        pass
        
    # Verify final delivery
    ok = verify_file('final.mp4')
    if ok:
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)
