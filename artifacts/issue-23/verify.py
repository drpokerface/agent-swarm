import os
import sys
import subprocess
import json
import time
import random
import shutil

subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "-q"])
from google import genai

def get_media_info(filepath):
    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", filepath]
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(result.stdout)
    except Exception as e:
        return None

def verify_file(filepath, is_fault=False):
    all_pass = True
    
    # C1
    if not os.path.exists(filepath):
        print(f"C1: FAIL - {filepath} does not exist")
        return False
    print(f"C1: PASS - {filepath} exists")

    info = get_media_info(filepath)
    if not info:
        print("C2-C4: FAIL - Could not parse media info")
        return False

    # C2
    duration = float(info.get('format', {}).get('duration', 0))
    if 110 <= duration <= 140:
        print(f"C2: PASS - Duration is {duration}s")
    else:
        print(f"C2: FAIL - Duration is {duration}s")
        all_pass = False

    # C4
    streams = info.get('streams', [])
    v_stream = next((s for s in streams if s.get('codec_type') == 'video'), None)
    a_stream = next((s for s in streams if s.get('codec_type') == 'audio'), None)

    if v_stream and a_stream:
        print("C4: PASS - AV streams present")
    else:
        print("C4: FAIL - Missing AV streams")
        all_pass = False

    # C3
    if v_stream:
        width = int(v_stream.get('width', 0))
        height = int(v_stream.get('height', 0))
        if width == 1280 and height == 720:
            print(f"C3: PASS - Resolution is {width}x{height}")
        else:
            print(f"C3: FAIL - Resolution is {width}x{height}")
            all_pass = False
    else:
        all_pass = False

    if is_fault or not all_pass:
        return all_pass

    # C5 & C6
    print("Uploading to Gemini for subjective check...")
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    video_file = client.files.upload(file=filepath)
    try:
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        if video_file.state.name == "FAILED":
            print("C5/C6: FAIL - Video processing failed in Gemini")
            return False
            
        rubric = '''
Evaluate this animated comedy short on Humor, Timing, and Cohesion (Family Guy/South Park style).
Also check if it is blank, silent, uniformly solid color, or truncated.
Rate 0 to 10. Pass threshold is 7.
Return JSON: {"score": 8, "reasoning": "...", "is_degenerate": false}
'''
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=[rubric, video_file],
            config={"response_mime_type": "application/json"}
        )
        data = json.loads(response.text)
        score = data.get("score", 0)
        is_degenerate = data.get("is_degenerate", True)
        
        if is_degenerate:
            print("C5: FAIL - Video is degenerate")
            all_pass = False
        else:
            print("C5: PASS - Video is not degenerate")
            
        if score >= 7:
            print(f"C6: PASS - Score {score} >= 7. Reasoning: {data.get('reasoning')}")
        else:
            print(f"C6: FAIL - Score {score} < 7. Reasoning: {data.get('reasoning')}")
            all_pass = False
            
    except Exception as e:
        print(f"C5/C6: FAIL - Gemini error: {e}")
        all_pass = False
    finally:
        try:
            client.files.delete(name=video_file.name)
        except:
            pass

    return all_pass

def main():
    print("--- FAULT PROOF ---")
    os.makedirs("scratch", exist_ok=True)
    fault_file = f"scratch/faulty_{random.randint(1000, 9999)}.mp4"
    if os.path.exists("final.mp4"):
        shutil.copy("final.mp4", fault_file)
        with open(fault_file, "r+b") as f:
            f.truncate(1024 * 100) # Truncate to 100KB to corrupt
    else:
        with open(fault_file, "wb") as f:
            f.write(b"garbage"*100)
            
    if verify_file(fault_file, is_fault=True):
        print("FAULT-PROOF: FAIL (Passed when it should have failed)")
        sys.exit(1)
    else:
        print("FAULT-PROOF: Caught induced fault")
        
    print("
--- VERIFICATION ---")
    if verify_file("final.mp4"):
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)

if __name__ == '__main__':
    main()
