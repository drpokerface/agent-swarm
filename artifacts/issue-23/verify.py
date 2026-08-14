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

    return os.path.exists(target), str(os.path.exists(target))



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

    

    client = genai.Client()

    try:

        video_file = client.files.upload(file=target)
        import time
        while True:
            video_file = client.files.get(name=video_file.name)
            if 'PROCESSING' in str(video_file.state).upper():
                time.sleep(2)
            else:
                break
        if 'FAILED' in str(video_file.state).upper():
            return False, 'Gemini processing failed'

        # Read rubric

        with open("rubric.md", "r") as f:

            rubric = f.read()

        

        prompt = f"""Review this animated comedy short against the rubric below.



{rubric}



Score the overall humor, timing, and cohesion from 0 to 10.

Is the score 7 or higher? Answer ONLY in this JSON format: {{"score": 7.5, "pass": true, "reason": "..."}}"""

        

        response = client.models.generate_content(

            model='gemini-3.5-flash',

            contents=[video_file, prompt],

            config=types.GenerateContentConfig(

                response_mime_type="application/json",

            )

        )

        result = json.loads(response.text)

        score = result.get("score", 0)

        passed = result.get("pass", False)

        

        # cleanup

        client.files.delete(name=video_file.name)

        

        return passed, f"Score: {score} - {result.get('reason', '')}"

    except Exception as e:

        return False, f"Perceptual check failed: {e}"



def main():

    print("Starting verification...")

    target = "final.mp4"

    probe = run_ffprobe(target)

    

    c1, m1 = check_c1(target)

    print(f"C1: {m1}")

    c2, m2 = check_c2(probe)

    print(f"C2: {m2}")

    c3, m3 = check_c3(probe)

    print(f"C3: {m3}")

    c4, m4 = check_c4(probe)

    print(f"C4: {m4}")

    c5, m5 = check_c5_perceptual(target)

    print(f"C5: {m5}")

    

    # Fault Proof

    print("\n--- FAULT PROOF ---")

    os.makedirs("scratch", exist_ok=True)

    bad_target = "scratch/bad_final.mp4"

    # Create a broken 1-second video

    subprocess.run(["ffmpeg", "-y", "-f", "lavfi", "-i", "color=c=red:s=640x480:d=1", "-vcodec", "libx264", bad_target], capture_output=True)

    bad_probe = run_ffprobe(bad_target)

    

    f_c2, f_m2 = check_c2(bad_probe)

    f_c3, f_m3 = check_c3(bad_probe)

    f_c4, f_m4 = check_c4(bad_probe)

    

    caught = (not f_c2) and (not f_c4)

    print(f"FAULT-PROOF: Tested 640x480 1s video with no audio. C2 caught: {f_m2} | C3 caught: {f_m3} | C4 caught: {f_m4}")

    

    if not caught:

        print("VERDICT: FAIL - Fault proof failed")

        sys.exit(1)

        

    if c1 and c2 and c3 and c4 and c5:

        print("VERDICT: PASS")

        sys.exit(0)

    else:

        print("VERDICT: FAIL")

        sys.exit(1)



if __name__ == '__main__':

    main()

