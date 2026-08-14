# VALIDATED: Caught fault -> Silent audio
import os
import subprocess
import json
import sys

try:
    from google import genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai"])
    from google import genai

def run_ffprobe(file_path):
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", file_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return None
    return json.loads(res.stdout)

def verify_artifact(file_path, is_fault=False):
    if not os.path.exists(file_path):
        return False, "File missing", {}
        
    info = run_ffprobe(file_path)
    if not info:
        return False, "ffprobe failed", {}
        
    streams = info.get("streams", [])
    fmt = info.get("format", {})
    
    has_video = False
    has_audio = False
    width, height = 0, 0
    duration = float(fmt.get("duration", 0))
    
    for s in streams:
        if s.get("codec_type") == "video":
            has_video = True
            width = int(s.get("width", 0))
            height = int(s.get("height", 0))
        elif s.get("codec_type") == "audio":
            has_audio = True
            
    stats = {
        "exists": True,
        "has_streams": has_video and has_audio,
        "width": width,
        "height": height,
        "duration": duration
    }
    
    if not stats["has_streams"]:
        return False, "Missing audio or video stream", stats
    if width != 1280 or height != 720:
        return False, f"Resolution {width}x{height}", stats
    if not (100 <= duration <= 140):
        return False, f"Duration {duration} out of bounds", stats
        
    # Audio volume check
    vol_cmd = ["ffmpeg", "-v", "info", "-i", file_path, "-af", "volumedetect", "-f", "null", "-"]
    vol_res = subprocess.run(vol_cmd, capture_output=True, text=True)
    if "mean_volume: -91" in vol_res.stderr or "mean_volume: -inf" in vol_res.stderr or "mean_volume: -100" in vol_res.stderr:
        return False, "Silent audio", stats

    if not is_fault:
        # Check perception
        os.makedirs("scratch/frames", exist_ok=True)
        mid_time = 15
        subprocess.run(["ffmpeg", "-y", "-ss", str(mid_time), "-i", file_path, "-vframes", "1", "scratch/frames/sample.jpg"], capture_output=True)
        
        if not os.path.exists("scratch/frames/sample.jpg"):
            return False, "Failed to extract sample frame", stats
            
        try:
            client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
            handle = client.files.upload(file="scratch/frames/sample.jpg")
            prompt = 'This is a sample frame. Does it depict a cohesive animated comedy short scene (e.g. characters, background) or is it a degenerate blank/solid frame? Reply ONLY with JSON: {"is_valid": true/false, "reason": "brief reason"}'
            resp = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[prompt, handle],
                config={"response_mime_type": "application/json"}
            ).text
            res_json = json.loads(resp)
            if not res_json.get("is_valid", False):
                return False, f"Model perception failed: {res_json.get('reason')}", stats
        except Exception as e:
            return False, f"Model check error: {e}", stats
            
    return True, "OK", stats

def main():
    print("EXPECT: Verify RED")
    
    # Fault Proof
    os.makedirs("scratch", exist_ok=True)
    fault_file = "scratch/fault.mp4"
    if not os.path.exists(fault_file):
        subprocess.run([
            "ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=black:s=1280x720:d=120",
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "120", fault_file
        ], capture_output=True)
    
    f_ok, f_msg, _ = verify_artifact(fault_file, is_fault=True)
    if not f_ok:
        print(f"FAULT-PROOF: Caught fault -> {f_msg}")
        try:
            with open(__file__, "r") as f:
                lines = f.readlines()
            if lines[0].startswith("# VALIDATED: False"):
                lines[0] = f"# VALIDATED: Caught fault -> {f_msg}\n"

                with open(__file__, "w") as f:
                    f.writelines(lines)
        except:
            pass
    else:
        print("FAULT-PROOF: Failed to catch degenerate video")
        sys.exit(1)
        
    target = "final.mp4"
    ok, msg, stats = verify_artifact(target)
    
    print(f"C1 (exists): {stats.get('exists', False)}")
    print(f"C2 (streams): {stats.get('has_streams', False)}")
    print(f"C3 (1280x720): {stats.get('width', 0)}x{stats.get('height', 0)}")
    print(f"C4 (duration 100-140s): {stats.get('duration', 0)}s")
    
    if ok:
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print(f"VERDICT: FAIL ({msg})")
        sys.exit(1)

if __name__ == '__main__':
    main()
