import os, sys, subprocess, json, random, shutil, time

def run_ffprobe(target):
    try:
        cmd = ["ffprobe", "-v", "quiet", "-print_format", "json", "-show_format", "-show_streams", target]
        res = subprocess.run(cmd, capture_output=True, text=True, check=True)
        return json.loads(res.stdout)
    except Exception as e:
        return None

def check_c1(target):
    if not os.path.exists(target): return False, "Missing"
    return True, "Exists"

def check_c2(probe):
    if not probe: return False, "No probe data"
    for s in probe.get("streams", []):
        if s.get("codec_type") == "video":
            w, h = s.get("width"), s.get("height")
            if w == 1280 and h == 720:
                return True, "1280x720"
            return False, f"{w}x{h}"
    return False, "No video stream"

def check_c3(probe):
    if not probe: return False, "No probe data"
    has_v = any(s.get("codec_type") == "video" for s in probe.get("streams", []))
    has_a = any(s.get("codec_type") == "audio" for s in probe.get("streams", []))
    return (has_v and has_a), f"Video:{has_v} Audio:{has_a}"

def check_c4(probe):
    if not probe: return False, "No probe data"
    fmt = probe.get("format", {})
    dur = float(fmt.get("duration", 0))
    if 100 <= dur <= 140:
        return True, f"{dur:.2f}s"
    return False, f"{dur:.2f}s"

def check_degenerate(target):
    if not os.path.exists(target): return False, "Missing"
    size = os.path.getsize(target)
    if size < 100000:
        return False, f"File too small ({size} bytes)"
    return True, "Passed size check"

def check_c5(target):
    if "GEMINI_API_KEY" not in os.environ:
        return False, "No API key"
    try:
        from google import genai
        client = genai.Client()
        video_file = client.files.upload(file=target)
        while True:
            video_file = client.files.get(name=video_file.name)
            if video_file.state.name == 'PROCESSING':
                time.sleep(2)
            elif video_file.state.name == 'FAILED':
                return False, "Video processing failed on Gemini"
            else:
                break
        
        with open("rubric.md", "r") as f:
            rubric = f.read()

        prompt = "Here is the rubric:
" + rubric + "
Review this video. Is it a cohesive comedy short that scores >= 7 on the rubric? Look for distinct scenes, audio, and pacing. Reply with exactly 'YES' or 'NO', followed by a brief reason."
        resp = client.models.generate_content(model="gemini-3.5-flash", contents=[prompt, video_file])
        ans = resp.text.strip()
        if ans.startswith("YES"):
            return True, ans
        return False, ans
    except Exception as e:
        return False, f"Model call failed: {e}"

def fault_proof():
    print("--- FAULT PROOF ---")
    os.makedirs("scratch", exist_ok=True)
    fault_target = "scratch/fault.mp4"
    with open(fault_target, "w") as f:
        f.write("junk data")
    c1, msg1 = check_c1(fault_target)
    probe = run_ffprobe(fault_target)
    c2, msg2 = check_c2(probe)
    c3, msg3 = check_c3(probe)
    c4, msg4 = check_c4(probe)
    deg, msg_deg = check_degenerate(fault_target)
    
    if not deg and not c2:
        print("VALIDATED: checks correctly caught the degenerate/corrupt video.")
    else:
        print("FAULT-PROOF FAILED.")
        sys.exit(1)

def main():
    target = "final.mp4"
    fault_proof()
    
    print("--- EVALUATION ---")
    c1, m1 = check_c1(target)
    print(f"C1: {c1} - {m1}")
    if not c1: sys.exit(1)
    
    probe = run_ffprobe(target)
    c2, m2 = check_c2(probe)
    print(f"C2: {c2} - {m2}")
    if not c2: sys.exit(1)
    
    c3, m3 = check_c3(probe)
    print(f"C3: {c3} - {m3}")
    if not c3: sys.exit(1)
    
    c4, m4 = check_c4(probe)
    print(f"C4: {c4} - {m4}")
    if not c4: sys.exit(1)
    
    deg, m_deg = check_degenerate(target)
    print(f"Degenerate Check: {deg} - {m_deg}")
    if not deg: sys.exit(1)
    
    c5, m5 = check_c5(target)
    print(f"C5: {c5} - {m5}")
    if not c5: sys.exit(1)
    
    print("VERDICT: PASS")

if __name__ == '__main__':
    main()
