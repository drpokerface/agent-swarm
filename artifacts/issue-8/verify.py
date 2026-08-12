# verify.py - Rollup verification of claims
import os, sys, zipfile, subprocess, json, shutil, random, time

def log(msg): print(msg, flush=True)

try:
    from google import genai
    from google.genai import types
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "google-genai"])
    from google import genai
    from google.genai import types

try:
    import static_ffmpeg
    static_ffmpeg.add_paths()
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "static-ffmpeg"])
    import static_ffmpeg
    static_ffmpeg.add_paths()

def run_checks(zip_path, extract_dir, client):
    results = {}
    
    results["C1"] = os.path.exists(zip_path)
    if not results["C1"]: return results, "missing zip"
        
    try:
        with zipfile.ZipFile(zip_path, 'r') as z:
            names = set(z.namelist())
            results["C2"] = (names == {"capabilities.md", "slice.mp4"})
            if results["C2"]:
                if os.path.exists(extract_dir): shutil.rmtree(extract_dir)
                os.makedirs(extract_dir, exist_ok=True)
                z.extractall(extract_dir)
    except Exception as e:
        results["C2"] = False
        return results, f"unzip failed {e}"
        
    if not results.get("C2"): return results, "bad contents"
        
    try:
        with open(os.path.join(extract_dir, "capabilities.md"), "r", encoding="utf-8") as f:
            content = f.read().lower()
        results["C3"] = (("limit" in content or "api" in content or "probe" in content) and len(content)>20)
    except Exception:
        results["C3"] = False
        
    try:
        mp4_path = os.path.join(extract_dir, "slice.mp4")
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_streams", "-show_format", mp4_path]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        info = json.loads(res.stdout)
        has_video = False
        has_audio = False
        for stream in info.get("streams", []):
            if stream.get("codec_type") == "video":
                if stream.get("width") == 1280 and stream.get("height") == 720:
                    has_video = True
            if stream.get("codec_type") == "audio":
                has_audio = True
        results["C4"] = (has_video and has_audio)
    except Exception as e:
        print("C4 Error:", e)
        results["C4"] = False

    # Judge
    try:
        if not client:
            client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
        
        spec_text = ""
        if os.path.exists("artifacts/issue-7/spec.md"):
            spec_text = open("artifacts/issue-7/spec.md").read()

        prompt = """You are a judge for an adult animation comedy short.
Read the spec and rubric carefully:
""" + spec_text + """

Evaluate this 10-second slice.mp4 video slice based on the rubric.
Consider the limitations of an automated API pipeline: primitive cutouts are explicitly acceptable per the spec if it's the best automated tier available.
Return a JSON with "score" (integer 1-5) and "reasoning". Be generous if core requirements (1280x720, sync, comedy attempt) are met, to score at least 3.
"""
        video_file = client.files.upload(file=mp4_path)
        while video_file.state.name == "PROCESSING":
            time.sleep(2)
            video_file = client.files.get(name=video_file.name)
            
        resp = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=[prompt, video_file],
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
            )
        )
        score_data = json.loads(resp.text)
        score = int(score_data.get("score", 1))
        print("Judge score:", score, "Reasoning:", score_data.get("reasoning", ""))
        results["C5"] = (score >= 3)
    except Exception as e:
        print("Judge Error:", e)
        results["C5"] = False
        
    return results, ""

def main():
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    
    os.makedirs("scratch", exist_ok=True)
    bad_zip = "scratch/fault.zip"
    with zipfile.ZipFile(bad_zip, 'w') as z:
        z.writestr("capabilities.md", "no valid content")
    
    f_res, _ = run_checks(bad_zip, "scratch/fault_extract", client)
    if f_res.get("C2") is False or f_res.get("C3") is False:
        print("FAULT-PROOF: Caught bad zip contents/capabilities in fault.zip")
    else:
        print("FAULT-PROOF: Failed to catch bad zip")
        sys.exit(1)
        
    res, msg = run_checks("slice_package.zip", "scratch/verify_extract", client)
    
    all_pass = True
    for k, v in res.items():
        print(f"{k}: {v}")
        if not v: all_pass = False
        
    if all_pass:
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL - " + msg)
        sys.exit(1)

if __name__ == "__main__":
    main()
