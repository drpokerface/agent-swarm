# VALIDATED: Caught fault -> Corrupted video missing streams
import os
import sys
import json
import random
import shutil
import subprocess

try:
    from google import genai
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "google-genai", "pillow"])
    from google import genai

def run_ffprobe(file_path):
    cmd = ["ffprobe", "-v", "error", "-show_streams", "-show_format", "-of", "json", file_path]
    res = subprocess.run(cmd, capture_output=True, text=True)
    if res.returncode != 0:
        return None
    try:
        return json.loads(res.stdout)
    except json.JSONDecodeError:
        return None

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
    if not (100 <= duration <= 145):
        return False, f"Duration {duration} out of bounds", stats
        
    # Audio volume check for degenerate silent audio
    vol_cmd = ["ffmpeg", "-v", "info", "-i", file_path, "-af", "volumedetect", "-f", "null", "-"]
    vol_res = subprocess.run(vol_cmd, capture_output=True, text=True)
    if "mean_volume: -91" in vol_res.stderr or "mean_volume: -inf" in vol_res.stderr or "mean_volume: -100" in vol_res.stderr:
        return False, "Silent audio", stats

    if not is_fault:
        # Check perception via Model
        os.makedirs("scratch/frames", exist_ok=True)
        mid_time = min(15, duration / 2)
        frame_path = "scratch/frames/sample_eval.jpg"
        subprocess.run(["ffmpeg", "-y", "-ss", str(mid_time), "-i", file_path, "-vframes", "1", frame_path], capture_output=True)
        
        if not os.path.exists(frame_path):
            return False, "Failed to extract perception frame", stats
            
        client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])
        try:
            uploaded_file = client.files.upload(file=frame_path)
            prompt = "Look at this frame from an animated comedy short. Does it depict a fully cohesive animated scene with characters or elements typical of a cartoon? Reply YES or NO, followed by a brief reason."
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=[uploaded_file, prompt]
            ).text
            if not response.strip().upper().startswith("YES"):
                return False, f"Perceptual check failed: {response}", stats
        except Exception as e:
            print(f"Model API error: {e}")
            return False, "Model API error", stats

    return True, "Pass", stats

def main():
    print("C1: final.mp4 exists, plays for ~120 seconds, resolution is exactly 1280x720, distinct streams")
    print("C2: Subjective quality and coherence (perceptual check)")

    # 1. Fault Proof
    os.makedirs("scratch", exist_ok=True)
    fault_path = f"scratch/fault_{random.randint(1000,9999)}.mp4"
    if os.path.exists("final.mp4"):
        shutil.copy("final.mp4", fault_path)
        # Corrupt file by writing garbage
        with open(fault_path, "wb") as f:
            f.write(b'0' * 1024)
            
        ok, msg, stats = verify_artifact(fault_path, is_fault=True)
        if not ok:
            print(f"FAULT-PROOF: Caught fault -> {msg}")
        else:
            print("FAULT-PROOF FAILED: Did not catch corruption!")
            sys.exit(1)
    else:
        print("FAULT-PROOF FAILED: final.mp4 does not exist to copy")
        sys.exit(1)

    # 2. Verify Actual Artifact
    ok, msg, stats = verify_artifact("final.mp4", is_fault=False)
    if ok:
        print(f"Measured Values: duration={stats['duration']}, width={stats['width']}, height={stats['height']}, streams={stats['has_streams']}")
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print(f"VERIFICATION FAILED: {msg}")
        sys.exit(1)

if __name__ == '__main__':
    main()
