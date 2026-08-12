# VERIFY SCRIPT - RED
import os
import subprocess
import zipfile
import json
import random
import time

def check(zip_path, run_judge=True):
    results = {}
    
    # C1: zip exists
    c1 = os.path.exists(zip_path)
    results['C1'] = c1
    print(f"C1 (zip exists): {c1}")
    if not c1: return results
    
    # Extract
    ext_dir = os.path.join(os.path.dirname(zip_path), f"ext_{random.randint(0, 999999)}")
    os.makedirs(ext_dir, exist_ok=True)
    try:
        with zipfile.ZipFile(zip_path, 'r') as zf:
            zf.extractall(ext_dir)
    except Exception as e:
        results['C2'] = False
        print(f"C2 (extractable and contains files): False - {e}")
        return results

    # C2: contains capabilities.md and slice.mp4
    files = os.listdir(ext_dir)
    c2 = 'capabilities.md' in files and 'slice.mp4' in files
    results['C2'] = c2
    print(f"C2 (contains capabilities.md and slice.mp4): {c2}")
    if not c2: return results
    
    # C3: 1280x720 video
    mp4_path = os.path.join(ext_dir, 'slice.mp4')
    try:
        cmd = ['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'json', mp4_path]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(proc.stdout)
        streams = info.get('streams', [])
        if streams:
            w = streams[0].get('width')
            h = streams[0].get('height')
            c3 = (w == 1280 and h == 720)
            print(f"C3 (1280x720 video): {c3} (Found {w}x{h})")
        else:
            c3 = False
            print(f"C3 (1280x720 video): False (No video stream)")
    except Exception as e:
        c3 = False
        print(f"C3 (1280x720 video): False - {e}")
    results['C3'] = c3

    # C4: audio track
    try:
        cmd = ['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_type', '-of', 'json', mp4_path]
        proc = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(proc.stdout)
        c4 = len(info.get('streams', [])) > 0
        print(f"C4 (audio track): {c4}")
    except Exception as e:
        c4 = False
        print(f"C4 (audio track): False - {e}")
    results['C4'] = c4

    # C5: judge >= 3/5
    c5 = False
    if run_judge:
        from google import genai
        try:
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
            
            # Read spec.md for context
            with open("artifacts/issue-7/spec.md", "r") as f:
                spec = f.read()

            video_file = client.files.upload(file=mp4_path)
            
            # Wait for processing
            while video_file.state.name == "PROCESSING":
                time.sleep(2)
                video_file = client.files.get(name=video_file.name)
                
            if video_file.state.name == "FAILED":
                print("C5: False (Video processing failed)")
            else:
                prompt = f'''
You are a blind judge. You evaluate this adult animation short slice.
Here is the spec and rubric:
{spec}

Rate the video strictly on the 1-5 scale based on the rubric. 
Respond with valid JSON only:
{{"score": <int>, "reason": "<string>"}}
'''
                response = client.models.generate_content(
                    model="gemini-3.5-flash",
                    contents=[video_file, prompt],
                    config={"response_mime_type": "application/json", "response_schema": {"type": "object", "properties": {"score": {"type": "integer"}, "reason": {"type": "string"}}}}
                )
                data = json.loads(response.text)
                score = data.get("score", 0)
                c5 = score >= 3
                print(f"C5 (judge >= 3/5): {c5} (Score: {score}, Reason: {data.get('reason')})")
        except Exception as e:
            print(f"C5: False - Exception during judging: {e}")
    else:
        c5 = True
        print(f"C5 (judge skip): {c5}")
    results['C5'] = c5
        
    return results

if __name__ == '__main__':
    print("# VERIFY SCRIPT")
    real_zip = 'slice_package.zip'
    
    print("Running FAULT-PROOF...")
    fault_dir = f"scratch/fault_{random.randint(0,999999)}"
    os.makedirs(fault_dir, exist_ok=True)
    fault_zip = os.path.join(fault_dir, 'slice_package.zip')
    # Create empty zip to fail C2
    with zipfile.ZipFile(fault_zip, 'w') as z:
        pass
    
    fault_res = check(fault_zip, run_judge=False)
    if not fault_res.get('C2'):
        print(f"FAULT-PROOF: Empty zip correctly caught failing C2.")
    else:
        print("FAULT-PROOF: Failed to catch empty zip.")
        exit(1)
        
    print("\nRunning REAL verification...")
    if not os.path.exists(real_zip):
        print(f"C1 (zip exists): False")
        print("VERDICT: FAIL")
        exit(1)
        
    res = check(real_zip)
    if all(res.values()):
        print("VERDICT: PASS")
    else:
        print("VERDICT: FAIL")
        exit(1)
