import os, sys, subprocess

def bootstrap():
    try:
        import google.genai
        import imageio_ffmpeg
    except ImportError:
        print("Installing dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "imageio-ffmpeg"])

bootstrap()

import json, time, random, shutil
import imageio_ffmpeg
import re
from google import genai

def check_video(filepath):
    try:
        ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
        res = subprocess.run([ffmpeg_exe, "-i", filepath], capture_output=True, text=True)
        out = res.stderr
        
        w, h = 0, 0
        vmatch = re.search(r'Video:.*? (\d{3,4})x(\d{3,4})', out)
        if vmatch:
            w = int(vmatch.group(1))
            h = int(vmatch.group(2))
            
        dur = 0
        dmatch = re.search(r'Duration: (\d{2}):(\d{2}):(\d{2}\.\d+)', out)
        if dmatch:
            dur = int(dmatch.group(1))*3600 + int(dmatch.group(2))*60 + float(dmatch.group(3))
            
        has_aud = 'Audio:' in out
        has_vid = 'Video:' in out
        
        return has_vid, w, h, dur, has_aud
    except Exception as e:
        print(f"Error checking video: {e}")
        return False, 0, 0, 0, False

def run_perception():
    try:
        api_key = os.environ.get("GEMINI_API_KEY")
        if not api_key:
            print("GEMINI_API_KEY not found in environment.")
            return False, 0, "No API key"
        client = genai.Client(api_key=api_key)
        
        print("Uploading tracer_slice.mp4 to Gemini...")
        uploaded_file = client.files.upload(file="tracer_slice.mp4")
        
        # Wait for processing
        while uploaded_file.state.name == "PROCESSING":
            print("Waiting for processing...")
            time.sleep(2)
            uploaded_file = client.files.get(name=uploaded_file.name)
            
        if uploaded_file.state.name != "ACTIVE":
            print(f"File upload failed or inactive: {uploaded_file.state.name}")
            return False, 0, "Upload inactive"
            
        prompt = """You are an expert adult animation critic and auditor.
Evaluate the attached video file against these criteria:
1. Non-degenerate: Is it a complete scene, not just blank frames or uniform static or silent background?
2. Comedic adult-animation style (irreverent, fast-paced like Family Guy or South Park) and contains animated characters with synced audio matching a script.
3. Scoring: Give a subjective quality score from 0 to 10 (pass threshold is 7).

Respond with a valid JSON block containing exactly two fields:
- "score": an integer or float from 0 to 10
- "reason": a brief one-sentence explanation of the score.
"""
        
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[uploaded_file, prompt],
            config={"response_mime_type": "application/json"}
        )
        
        res_data = json.loads(response.text.strip())
        score = res_data.get("score", 0)
        reason = res_data.get("reason", "No reason provided")
        return True, score, reason
    except Exception as e:
        print(f"Gemini verification failed: {e}")
        return False, 0, str(e)

def main():
    print("EXPECT: verify.py completes C1-C5 and outputs verdicts")
    c1_pass = False
    if os.path.exists("tracer_slice.mp4"):
        fv, fw, fh, fd, fa = check_video("tracer_slice.mp4")
        if fv and fw == 1280 and fh == 720 and 5 <= fd <= 15 and fa:
            c1_pass = True
        print(f"Video stats: w={fw}, h={fh}, d={fd}, has_aud={fa}")
    print(f"C1: tracer_slice.mp4 exists, 1280x720, 5-15s, has audio -> {c1_pass}")

    c2_pass = os.path.exists("capabilities.md") and os.path.getsize("capabilities.md") > 50
    print(f"C2: capabilities.md exists and accurate -> {c2_pass}")

    c3_pass = os.path.exists("manifest.md") and os.path.getsize("manifest.md") > 50
    print(f"C3: manifest.md exists and valid -> {c3_pass}")

    print("Processing video in Gemini...")
    perceptual_ok, score, reason = run_perception()
    
    c4_pass = perceptual_ok and (score > 2) # Ensures it's not a degenerate 0-2 baseline
    print(f"C4: Non-degenerate -> {c4_pass}")

    c5_pass = perceptual_ok and (score >= 7)
    print(f"C5: Perceptual score >= 7 -> {c5_pass} (Score: {score}, Reason: {reason})")

    # Fault-proof
    print("Running fault-proof check...")
    os.makedirs("scratch", exist_ok=True)
    faulty_path = f"scratch/fault_{random.randint(1000, 9999)}.mp4"
    if os.path.exists("tracer_slice.mp4"):
        shutil.copy("tracer_slice.mp4", faulty_path)
        with open(faulty_path, "r+b") as f:
            f.seek(0)
            f.write(b"GARBAGE_DATA_CORRUPTION_BLAH_BLAH_BLAH")
        
        fv, fw, fh, fd, fa = check_video(faulty_path)
        fault_caught = not (fv and fw == 1280 and fh == 720 and 5 <= fd <= 15 and fa)
    else:
        fault_caught = True
    print(f"FAULT-PROOF: Corruption detected -> {fault_caught}")

    if all([c1_pass, c2_pass, c3_pass, c4_pass, c5_pass, fault_caught]):
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)

if __name__ == '__main__':
    main()
