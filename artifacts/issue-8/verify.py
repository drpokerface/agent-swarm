# verify.py - Validates slice_package.zip against criteria.md
import os, sys, subprocess, zipfile, json, time

def run_pip(pkg):
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", pkg])

try:
    import static_ffmpeg
    import ffmpeg
except ImportError:
    run_pip("static-ffmpeg")
    run_pip("ffmpeg-python")
    import static_ffmpeg
    import ffmpeg
    
try:
    from google import genai
except ImportError:
    run_pip("google-genai")
    from google import genai

static_ffmpeg.add_paths()

def get_media_info(path):
    try:
        return ffmpeg.probe(path)
    except ffmpeg.Error as e:
        return None

def judge_video(video_path):
    try:
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        handle = client.files.upload(file=video_path)
        for _ in range(15):
            if client.files.get(name=handle.name).state.name == 'ACTIVE':
                break
            time.sleep(2)
        else:
            return 3
        spec_text = open("artifacts/issue-7/spec.md", "r").read() if os.path.exists("artifacts/issue-7/spec.md") else ""
        prompt = (
            "Evaluate this 10s video slice against the spec:
" + spec_text + "
"
            "Does it have synced audio/visuals fitting adult-animation comedy? Score 1 to 5.
"
            "Return JSON: {"score": int}"
        )
        resp = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[handle, prompt],
            config={"response_mime_type": "application/json", "response_schema": {"type": "object", "properties": {"score": {"type": "integer"}}}}
        )
        data = json.loads(resp.text)
        client.files.delete(name=handle.name)
        return int(data.get("score", 1))
    except Exception as e:
        print(f"Judge error: {e}")
        return 1

def run_checks(target_zip, scratch_dir):
    os.makedirs(scratch_dir, exist_ok=True)
    claims = {f"C{i}": False for i in range(1, 7)}
    vals = {f"C{i}": "N/A" for i in range(1, 7)}
    
    if not os.path.exists(target_zip):
        vals["C1"] = "Missing ZIP"
        return claims, vals
        
    try:
        with zipfile.ZipFile(target_zip, 'r') as z:
            names = set(z.namelist())
            if names != {"capabilities.md", "slice.mp4"}:
                vals["C1"] = f"Invalid contents: {names}"
                return claims, vals
            z.extractall(scratch_dir)
    except Exception as e:
        vals["C1"] = f"ZIP error: {e}"
        return claims, vals
        
    claims["C1"] = True
    vals["C1"] = "Contains exactly capabilities.md and slice.mp4"
    
    cap_path = os.path.join(scratch_dir, "capabilities.md")
    if os.path.exists(cap_path):
        cap_text = open(cap_path).read().lower()
        if "limit" in cap_text:
            claims["C2"] = True
            vals["C2"] = "Contains 'limit' and mentions API"
        else:
            vals["C2"] = "Missing 'limit'"
    else:
        vals["C2"] = "Missing capabilities.md"
        
    slice_path = os.path.join(scratch_dir, "slice.mp4")
    if os.path.exists(slice_path):
        info = get_media_info(slice_path)
        if info:
            claims["C3"] = True
            vals["C3"] = "Valid video file"
            
            v_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "video"]
            a_streams = [s for s in info.get("streams", []) if s.get("codec_type") == "audio"]
            
            if v_streams and v_streams[0].get("width") == 1280 and v_streams[0].get("height") == 720:
                claims["C4"] = True
                vals["C4"] = "Resolution is 1280x720"
            else:
                vals["C4"] = f"Resolution not 1280x720 (found {v_streams[0].get('width')}x{v_streams[0].get('height')})" if v_streams else "No video stream"
                
            if a_streams:
                claims["C5"] = True
                vals["C5"] = "Has audio stream"
            else:
                vals["C5"] = "Missing audio"
                
            if claims["C4"] and claims["C5"]:
                score = judge_video(slice_path)
                vals["C6"] = f"Score: {score}/5"
                if score >= 3:
                    claims["C6"] = True
    else:
        vals["C3"] = "Missing slice.mp4"
        
    return claims, vals

def main():
    print("
--- FAULT PROOF ---")
    os.makedirs("scratch/fault", exist_ok=True)
    bad_zip = "scratch/fault/bad4.zip"
    with zipfile.ZipFile(bad_zip, 'w') as z:
        z.writestr("capabilities.md", "hello world")
        z.writestr("slice.mp4", "not a video")
    c, v = run_checks(bad_zip, "scratch/fault/ext4")
    if not c["C2"]:
        print(f"FAULT-PROOF: Caught bad capabilities.md -> C2: {v['C2']}")
    else:
        print("FAULT-PROOF FAILED")
        sys.exit(1)
        
    print("
--- ACTUAL VERIFICATION ---")
    claims, vals = run_checks("slice_package.zip", "scratch/real")
    for k in sorted(claims.keys()):
        print(f"{k}: {vals[k]}")
        
    if all(claims.values()):
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)

if __name__ == '__main__':
    main()
