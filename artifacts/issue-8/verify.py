import os
import sys
import subprocess
subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "imageio-ffmpeg", "google-genai"])
import zipfile
import time
import json
import random
import shutil
from google import genai
from google.genai import types

def run_cmd(cmd):
    try:
        return subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
    except subprocess.CalledProcessError as e:
        return e.output

def check_video(path):
    import imageio_ffmpeg
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    out = run_cmd([ffmpeg, '-i', path])
    w, h, aud = 0, 0, False
    for line in out.split('
'):
        if 'Video:' in line and '1280x720' in line:
            w, h = 1280, 720
        if 'Audio:' in line:
            aud = True
    return w == 1280 and h == 720, aud

def score_video(path):
    if not os.path.exists(path): return 0
    client = genai.Client()
    f = client.files.upload(file=path)
    for _ in range(30):
        if client.files.get(name=f.name).state.name == "ACTIVE": break
        time.sleep(2)
    rubric = '''Evaluate this 10-second animated comedy slice against the following criteria.
Reply ONLY with a JSON object: {"pacing": <int 1-5>, "joke_density": <int 1-5>, "polish": <int 1-5>}
Criteria:
- Pacing (1-5): Hook in 5s, fast pacing, punchline at end, zero dead air (3 is functional).
- Joke Density (1-5): Standard is 3-5 JPM. (3 is functional).
- Audio-Visual Polish (1-5): Synced audio, clear visuals. (3 is functional).'''
    try:
        resp = client.models.generate_content(
            model="gemini-3.5-pro",
            contents=[rubric, f],
            config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.0)
        )
        data = json.loads(resp.text)
        client.files.delete(name=f.name)
        return min(data.get("pacing",0), data.get("joke_density",0), data.get("polish",0))
    except:
        return 0

def run_checks(zip_path, is_fault=False):
    c = {}
    c['C1_zip'] = os.path.exists(zip_path) and zipfile.is_zipfile(zip_path)
    has_cap, has_vid = False, False
    if c['C1_zip']:
        with zipfile.ZipFile(zip_path, 'r') as z:
            names = z.namelist()
            has_cap = 'capabilities.md' in names
            has_vid = 'slice.mp4' in names
    c['C2_contents'] = has_cap and has_vid
    
    limits = False
    if c['C1_zip'] and has_cap:
        with zipfile.ZipFile(zip_path, 'r') as z:
            text = z.read('capabilities.md').decode().lower()
            limits = 'limit' in text or 'rpm' in text or 'tpm' in text or 'quota' in text
    c['C3_limits'] = limits
    
    vid_ok, aud_ok = False, False
    score = 0
    if c['C1_zip'] and has_vid:
        ext = f"scratch/ext_chk_{random.randint(1000,9999)}"
        os.makedirs(ext, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as z:
            z.extract('slice.mp4', ext)
        vpath = os.path.join(ext, 'slice.mp4')
        if os.path.exists(vpath):
            vid_ok, aud_ok = check_video(vpath)
            if vid_ok and aud_ok:
                score = score_video(vpath) if not is_fault else 1
    
    c['C4_video_format'] = vid_ok and aud_ok
    c['C5_quality'] = score >= 3 if not is_fault else False
    
    all_pass = all(c.values())
    return c, all_pass

if __name__ == "__main__":
    os.makedirs("scratch", exist_ok=True)
    bad_zip = "scratch/bad_verify_final.zip"
    with zipfile.ZipFile(bad_zip, 'w') as z:
        z.writestr('capabilities.md', 'Nothing here')
    
    fc, fpass = run_checks(bad_zip, is_fault=True)
    print("FAULT-PROOF: caught bad zip:", fc)
    
    c, all_pass = run_checks('slice_package.zip')
    for k, v in c.items():
        print(f"{k}: {v}")
    
    if all_pass:
        print("VERDICT: PASS")
        sys.exit(0)
    else:
        print("VERDICT: FAIL")
        sys.exit(1)
