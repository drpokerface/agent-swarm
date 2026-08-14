import os, json, time, random, shutil, subprocess, sys
from google import genai
from google.genai import types

def run_cmd(cmd):
    try:
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return res.stdout
    except Exception:
        return None

def check_video(path):
    if not os.path.exists(path): return False, 0, 0, 0, False
    out = run_cmd(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=noprint_wrappers=1:nokey=1', path])
    if out is None: return False, 0, 0, 0, False
    try: duration = float(out.strip())
    except: return False, 0, 0, 0, False
    out = run_cmd(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width,height', '-of', 'csv=s=x:p=0', path])
    if out is None: return False, 0, 0, 0, False
    try: width, height = map(int, out.strip().split('x'))
    except: return False, 0, 0, 0, False
    out = run_cmd(['ffprobe', '-v', 'error', '-select_streams', 'a:0', '-show_entries', 'stream=codec_type', '-of', 'default=noprint_wrappers=1:nokey=1', path])
    has_audio = out is not None and 'audio' in out.strip()
    return True, width, height, duration, has_audio

def run_perceptual(path):
    client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))
    video_file = client.files.upload(file=path)
    while video_file.state.name == 'PROCESSING':
        time.sleep(2)
        video_file = client.files.get(name=video_file.name)
    if video_file.state.name == 'FAILED':
        return {"blank": True, "animated_characters": False, "has_voice": False, "score": 0}
    
    prompt = "Watch this clip. Reply in strictly valid JSON: {'blank': boolean, 'animated_characters': boolean, 'has_voice': boolean, 'score': number}. 'blank' is true if the screen is entirely blank, uniform, or just static text. 'animated_characters' is true if characters are shown. 'has_voice' is true if a voice is heard. 'score' is from 0 to 10 for adult animation comedic pacing, style match (like Family Guy/South Park), and audio-visual sync."
    
    response = client.models.generate_content(
        model='gemini-3.5-flash',
        contents=[prompt, video_file],
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.0)
    )
    return json.loads(response.text)

def main():
    valid, w, h, d, has_audio = check_video('tracer_slice.mp4')
    c1_pass = valid and w == 1280 and h == 720 and 5 <= d <= 15 and has_audio
    print(f"C1: tracer_slice.mp4 exists, 1280x720, 5-15s, audio -> {c1_pass}")
    
    c2_pass = os.path.exists('capabilities.md') and 'gemini' in open('capabilities.md').read().lower()
    print(f"C2: capabilities.md exists and contains findings -> {c2_pass}")
    
    c3_pass = os.path.exists('manifest.md') and 'tracer_slice.mp4' in open('manifest.md').read()
    print(f"C3: manifest.md exists and lists files -> {c3_pass}")
    
    c4_pass = c5_pass = False
    if c1_pass:
        try:
            perc = run_perceptual('tracer_slice.mp4')
            c4_pass = not perc.get('blank', True) and perc.get('has_voice', False)
            c5_pass = perc.get('score', 0) >= 7 and perc.get('animated_characters', False)
            print(f"C4: Non-degenerate -> {c4_pass}")
            print(f"C5: Perceptual score >= 7 -> {c5_pass} (Score: {perc.get('score')})")
        except Exception as e:
            print(f"C4/C5 Perceptual exception: {e}")
    else:
        print("C4/C5 skipped")
        
    os.makedirs("scratch", exist_ok=True)
    fault_path = f"scratch/fault_{random.randint(1000, 9999)}.mp4"
    if os.path.exists('tracer_slice.mp4'):
        shutil.copy('tracer_slice.mp4', fault_path)
        with open(fault_path, 'r+b') as f:
            f.seek(0)
            f.write(b'GARBAGE')
            f.truncate()
        fv, fw, fh, fd, fa = check_video(fault_path)
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
